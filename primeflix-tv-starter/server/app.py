"""PrimeFlix TV: serveur MVP de licences et d'essai 10 minutes.

AVERTISSEMENT: démonstrateur de backend. Renforcer identité des appareils,
protection anti-bruteforce, journalisation et attestation avant mise en production.
"""

from __future__ import annotations

import calendar
import hashlib
import hmac
import os
import secrets
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, ForeignKey, String, create_engine, select, update, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


def add_calendar_months(source: datetime, months: int) -> datetime:
    source = aware(source)
    month_no = source.year * 12 + source.month - 1 + months
    year, month_zero = divmod(month_no, 12)
    month = month_zero + 1
    day = min(source.day, calendar.monthrange(year, month)[1])
    return source.replace(year=year, month=month, day=day)


def secret_env(name: str) -> str:
    value = os.environ.get(name, "")
    if len(value) < 16:
        raise RuntimeError(f"Configurer {name} avec au moins 16 caractères.")
    return value


IS_VERCEL = os.environ.get("VERCEL") == "1"
CONFIGURED_DATABASE_URL = os.environ.get("DATABASE_URL")
if IS_VERCEL and not CONFIGURED_DATABASE_URL:
    raise RuntimeError("DATABASE_URL PostgreSQL doit être configurée dans Vercel.")
ADMIN_KEY = secret_env("ADMIN_KEY")
CODE_PEPPER = secret_env("CODE_PEPPER")
TOKEN_PEPPER = secret_env("TOKEN_PEPPER")
DEVICE_PEPPER = secret_env("DEVICE_PEPPER")
DATABASE_URL = CONFIGURED_DATABASE_URL or "sqlite:///./primeflix.db"
IS_SQLITE = DATABASE_URL.startswith("sqlite")
if IS_VERCEL and IS_SQLITE:
    raise RuntimeError("Vercel requiert PostgreSQL persistant ; SQLite local n'est pas pris en charge.")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if IS_SQLITE else {},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Device(Base):
    __tablename__ = "devices"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    fingerprint_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    trial_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    subscription_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    subscription_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class ActivationCode(Base):
    __tablename__ = "activation_codes"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    code_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    plan: Mapped[str] = mapped_column(String(10), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    redeemed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    redeemed_device_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("devices.id"), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    target_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


app = FastAPI(title="PrimeFlix TV Licensing API", version="0.1.0")
allowed_origins = [item.strip() for item in os.environ.get("ADMIN_ORIGINS", "http://127.0.0.1:5173").split(",") if item.strip()]
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_credentials=False,
                   allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type", "X-Admin-Key"])

# Basic per-process throttling. Production must use a shared store (e.g. Redis)
# behind a trusted proxy; this is intentionally only a proportional MVP guard.
_attempts: dict[str, list[float]] = {}


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    if request.url.path in {"/v1/devices/register", "/v1/activate", "/v1/admin/codes"}:
        now = time.monotonic()
        key = (request.client.host if request.client else "unknown") + request.url.path
        bucket = [stamp for stamp in _attempts.get(key, []) if now - stamp < 60]
        limit = 12 if request.url.path != "/v1/admin/codes" else 6
        if len(bucket) >= limit:
            return JSONResponse({"detail": "Trop de tentatives. Réessayez dans une minute."}, status_code=429)
        bucket.append(now)
        _attempts[key] = bucket
    return await call_next(request)


def db_session():
    with SessionLocal() as db:
        yield db


def digest(value: str, pepper: str) -> str:
    return hmac.new(pepper.encode(), value.encode(), hashlib.sha256).hexdigest()


def assert_admin(x_admin_key: str | None = Header(default=None)):
    if not x_admin_key or not hmac.compare_digest(x_admin_key, ADMIN_KEY):
        raise HTTPException(status_code=401, detail="Accès administrateur refusé.")


def audit(db: Session, action: str, target_id: str | None = None) -> None:
    db.add(AuditLog(id=str(uuid.uuid4()), action=action, target_id=target_id, created_at=utcnow()))


def auth_device(
    authorization: str | None = Header(default=None),
    db: Session = Depends(db_session),
) -> Device:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Jeton d'appareil manquant.")
    token = authorization[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Jeton d'appareil vide.")
    device = db.scalar(select(Device).where(Device.token_hash == digest(token, TOKEN_PEPPER)))
    if not device:
        raise HTTPException(status_code=401, detail="Appareil non reconnu.")
    return device


class RegisterBody(BaseModel):
    # Sur Android TV, utiliser idéalement ANDROID_ID + attestation/compte.
    # Une valeur auto-déclarée ne prouve PAS l'identité de l'appareil.
    device_fingerprint: str = Field(min_length=8, max_length=200)


class CodeBody(BaseModel):
    code: str = Field(min_length=12, max_length=50)


class IssueBody(BaseModel):
    plan: Literal["monthly", "yearly"]
    quantity: int = Field(ge=1, le=100)


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/v1/devices/register", status_code=201)
def register(body: RegisterBody, db: Session = Depends(db_session)):
    fp_hash = digest(body.device_fingerprint, DEVICE_PEPPER)
    existing = db.scalar(select(Device).where(Device.fingerprint_hash == fp_hash))
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Appareil déjà enregistré. Réutiliser son jeton ou contacter l'administrateur.",
        )
    token = secrets.token_urlsafe(32)
    device = Device(
        id=str(uuid.uuid4()),
        fingerprint_hash=fp_hash,
        token_hash=digest(token, TOKEN_PEPPER),
        trial_started_at=utcnow(),
        subscription_expires_at=None,
    )
    db.add(device)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="Appareil déjà enregistré.")
    return {
        "device_id": device.id,
        "device_token": token,  # secret, à stocker localement de façon sûre
        "trial_seconds": 600,
        "server_now": utcnow().isoformat(),
    }


def access_payload(device: Device) -> dict:
    now = utcnow()
    subscription_end = aware(device.subscription_expires_at)
    trial_end = aware(device.trial_started_at) + timedelta(minutes=10)
    if device.subscription_revoked:
        state = "expired"
    elif subscription_end and subscription_end > now:
        state = "active"
    elif now < trial_end:
        state = "trial"
    else:
        state = "expired"
    return {
        "status": state,
        "allowed": state != "expired",
        "trial_seconds_remaining": max(0, int((trial_end - now).total_seconds())) if state == "trial" else 0,
        "subscription_expires_at": subscription_end.isoformat() if subscription_end else None,
        "server_now": now.isoformat(),
    }


@app.get("/v1/access")
def access(device: Device = Depends(auth_device)):
    return access_payload(device)


@app.post("/v1/playback/authorize")
def authorize_playback(device: Device = Depends(auth_device)):
    # Le serveur qui livre réellement les flux doit appliquer CE contrôle.
    result = access_payload(device)
    if not result["allowed"]:
        raise HTTPException(status_code=403, detail="Essai terminé ou abonnement expiré.")
    return {"allowed": True, "status": result["status"], "server_now": result["server_now"]}


@app.post("/v1/activate")
def activate(
    body: CodeBody,
    device: Device = Depends(auth_device),
    db: Session = Depends(db_session),
):
    code_hash = digest(body.code.strip().upper(), CODE_PEPPER)
    record = db.scalar(select(ActivationCode).where(ActivationCode.code_hash == code_hash))
    if not record:
        raise HTTPException(status_code=400, detail="Code invalide.")
    if record.redeemed_at is not None or record.revoked_at is not None:
        raise HTTPException(status_code=409, detail="Ce code a déjà été utilisé.")

    now = utcnow()
    # Compare-and-set côté SQL : empêcher la double consommation d'un même code.
    claimed = db.execute(
        update(ActivationCode)
        .where(ActivationCode.id == record.id, ActivationCode.redeemed_at.is_(None))
        .values(redeemed_at=now, redeemed_device_id=device.id)
    )
    if claimed.rowcount != 1:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ce code a déjà été utilisé.")

    current_end = aware(device.subscription_expires_at)
    start = max(now, current_end) if current_end else now
    months = 1 if record.plan == "monthly" else 12
    device.subscription_expires_at = add_calendar_months(start, months)
    device.subscription_revoked = False
    audit(db, "subscription.activated", device.id)
    db.add(device)
    db.commit()
    db.refresh(device)
    return {"plan": record.plan, **access_payload(device)}


@app.post("/v1/admin/codes", dependencies=[Depends(assert_admin)])
def issue_codes(body: IssueBody, db: Session = Depends(db_session)):
    prefix = "PFM" if body.plan == "monthly" else "PFY"
    codes = []
    now = utcnow()
    for _ in range(body.quantity):
        # 80 bits d'aléa. Codes divulgués UNE SEULE FOIS dans cette réponse.
        rand = secrets.token_hex(10).upper()
        code = prefix + "-" + "-".join(rand[i : i + 5] for i in range(0, 20, 5))
        db.add(ActivationCode(
            id=str(uuid.uuid4()),
            code_hash=digest(code, CODE_PEPPER),
            plan=body.plan,
            issued_at=now,
        ))
        codes.append(code)
    audit(db, "codes.issued", None)
    db.commit()
    return {"plan": body.plan, "quantity": len(codes), "codes": codes}


@app.get("/v1/admin/devices", dependencies=[Depends(assert_admin)])
def admin_devices(db: Session = Depends(db_session)):
    return [{"device_id": d.id, "status": access_payload(d)["status"],
             "trial_started_at": aware(d.trial_started_at).isoformat(),
             "subscription_expires_at": aware(d.subscription_expires_at).isoformat() if d.subscription_expires_at else None}
            for d in db.scalars(select(Device).order_by(Device.trial_started_at.desc())).all()]


@app.get("/v1/admin/codes", dependencies=[Depends(assert_admin)])
def admin_codes(db: Session = Depends(db_session)):
    return [{"id": c.id, "plan": c.plan, "issued_at": aware(c.issued_at).isoformat(),
             "redeemed_at": aware(c.redeemed_at).isoformat() if c.redeemed_at else None,
             "redeemed_device_id": c.redeemed_device_id,
             "status": "revoked" if c.revoked_at else ("used" if c.redeemed_at else "issued")}
            for c in db.scalars(select(ActivationCode).order_by(ActivationCode.issued_at.desc())).all()]


@app.get("/v1/admin/audit", dependencies=[Depends(assert_admin)])
def admin_audit(db: Session = Depends(db_session)):
    return [{"action": a.action, "target_id": a.target_id, "created_at": aware(a.created_at).isoformat()}
            for a in db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(500)).all()]


@app.post("/v1/admin/codes/{code_id}/revoke", dependencies=[Depends(assert_admin)])
def admin_revoke_code(code_id: str, db: Session = Depends(db_session)):
    code = db.get(ActivationCode, code_id)
    if not code:
        raise HTTPException(status_code=404, detail="Code introuvable.")
    if code.redeemed_at:
        raise HTTPException(status_code=409, detail="Code déjà activé ; révoquer l'abonnement associé.")
    code.revoked_at = utcnow()
    audit(db, "codes.revoked", code.id)
    db.commit()
    return {"status": "revoked"}


@app.post("/v1/admin/devices/{device_id}/revoke", dependencies=[Depends(assert_admin)])
def admin_revoke_subscription(device_id: str, db: Session = Depends(db_session)):
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Appareil introuvable.")
    device.subscription_revoked = True
    audit(db, "subscription.revoked", device.id)
    db.commit()
    return {"status": access_payload(device)["status"]}


@app.post("/v1/admin/devices/{device_id}/restore", dependencies=[Depends(assert_admin)])
def admin_restore_subscription(device_id: str, db: Session = Depends(db_session)):
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Appareil introuvable.")
    device.subscription_revoked = False
    audit(db, "subscription.restored", device.id)
    db.commit()
    return {"status": access_payload(device)["status"]}


class ResetBody(BaseModel):
    device_fingerprint: str = Field(min_length=8, max_length=200)


@app.post("/v1/admin/devices/reissue-token", dependencies=[Depends(assert_admin)])
def admin_reissue_token(body: ResetBody, db: Session = Depends(db_session)):
    """Support pour réinstallation : nouveau jeton, essai NON réinitialisé."""
    device = db.scalar(select(Device).where(Device.fingerprint_hash == digest(body.device_fingerprint, DEVICE_PEPPER)))
    if not device:
        raise HTTPException(status_code=404, detail="Appareil non trouvé.")
    token = secrets.token_urlsafe(32)
    device.token_hash = digest(token, TOKEN_PEPPER)
    db.commit()
    return {"device_id": device.id, "device_token": token, "access": access_payload(device)}
