import os
import tempfile
from datetime import datetime, timedelta, timezone
import importlib

path = tempfile.mktemp(suffix='.db')
os.environ['DATABASE_URL'] = 'sqlite:///' + path
os.environ['ADMIN_KEY'] = 'testing-admin-key-strong-value'
os.environ['CODE_PEPPER'] = 'testing-code-pepper-strong-value'
os.environ['TOKEN_PEPPER'] = 'testing-token-pepper-strong-value'
os.environ['DEVICE_PEPPER'] = 'testing-device-pepper-strong-value'

from fastapi.testclient import TestClient
from server.app import app, Base, engine, SessionLocal, Device, utcnow, add_calendar_months

Base.metadata.create_all(bind=engine)

client = TestClient(app)
licensing = importlib.import_module('server.app')


def test_trial_code_expiry_and_reinstall():
    r = client.post('/v1/devices/register', json={'device_fingerprint': 'tv-android-id-123456789'})
    assert r.status_code == 201, r.text
    token = r.json()['device_token']
    device_id = r.json()['device_id']
    headers = {'Authorization': 'Bearer ' + token}

    r = client.get('/v1/access', headers=headers)
    assert r.json()['status'] == 'trial'
    assert 0 < r.json()['trial_seconds_remaining'] <= 600

    r = client.post('/v1/devices/register', json={'device_fingerprint': 'tv-android-id-123456789'})
    assert r.status_code == 409  # le compteur ne redémarre pas

    with SessionLocal() as db:
        device = db.get(Device, device_id)
        device.trial_started_at = utcnow() - timedelta(minutes=11)
        db.commit()
    assert client.get('/v1/access', headers=headers).json()['status'] == 'expired'
    assert client.post('/v1/playback/authorize', headers=headers).status_code == 403

    assert client.post('/v1/activate', json={'code': 'PFM-INVALID-00000-00000-00000'}, headers=headers).status_code == 400

    admin = {'x-admin-key': os.environ['ADMIN_KEY']}
    code_r = client.post('/v1/admin/codes', json={'plan': 'monthly', 'quantity': 1}, headers=admin)
    assert code_r.status_code == 200
    code = code_r.json()['codes'][0]
    assert code.startswith('PFM-')
    activate_r = client.post('/v1/activate', json={'code': code}, headers=headers)
    assert activate_r.status_code == 200, activate_r.text
    assert activate_r.json()['status'] == 'active'
    assert client.post('/v1/activate', json={'code': code}, headers=headers).status_code == 409

    yearly = client.post('/v1/admin/codes', json={'plan': 'yearly', 'quantity': 1}, headers=admin).json()['codes'][0]
    yearly_activation = client.post('/v1/activate', json={'code': yearly}, headers=headers)
    assert yearly_activation.status_code == 200, yearly_activation.text
    assert yearly_activation.json()['plan'] == 'yearly'
    assert yearly_activation.json()['status'] == 'active'

    assert client.get('/v1/admin/devices', headers=admin).status_code == 200
    assert client.get('/v1/admin/codes', headers=admin).status_code == 200
    assert client.get('/v1/admin/audit', headers=admin).status_code == 200
    assert client.get('/v1/admin/devices').status_code == 401
    assert client.post(f'/v1/admin/devices/{device_id}/revoke', headers=admin).status_code == 200
    assert client.post('/v1/playback/authorize', headers=headers).status_code == 403
    assert client.post(f'/v1/admin/devices/{device_id}/restore', headers=admin).status_code == 200

    # Réinstallation avec aide support : abonnement conservé, token d'origine invalidé
    rec = client.post('/v1/admin/devices/reissue-token', json={'device_fingerprint': 'tv-android-id-123456789'}, headers=admin)
    assert rec.status_code == 200
    assert rec.json()['access']['status'] == 'active'
    assert client.get('/v1/access', headers=headers).status_code == 401
    new_h = {'Authorization': 'Bearer ' + rec.json()['device_token']}
    assert client.get('/v1/access', headers=new_h).json()['status'] == 'active'


def test_yearly_activation_and_renewal_are_twelve_calendar_months(monkeypatch):
    fixed = datetime(2024, 1, 31, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(licensing, 'utcnow', lambda: fixed)
    admin = {'x-admin-key': os.environ['ADMIN_KEY']}
    r = client.post('/v1/devices/register', json={'device_fingerprint': 'tv-yearly-test-987654321'})
    assert r.status_code == 201, r.text
    headers = {'Authorization': 'Bearer ' + r.json()['device_token']}

    first = client.post('/v1/admin/codes', json={'plan': 'yearly', 'quantity': 1}, headers=admin).json()['codes'][0]
    active = client.post('/v1/activate', json={'code': first}, headers=headers)
    assert active.status_code == 200, active.text
    assert datetime.fromisoformat(active.json()['subscription_expires_at']) == datetime(2025, 1, 31, 12, 0, tzinfo=timezone.utc)

    renewal = client.post('/v1/admin/codes', json={'plan': 'yearly', 'quantity': 1}, headers=admin).json()['codes'][0]
    renewed = client.post('/v1/activate', json={'code': renewal}, headers=headers)
    assert renewed.status_code == 200, renewed.text
    assert datetime.fromisoformat(renewed.json()['subscription_expires_at']) == datetime(2026, 1, 31, 12, 0, tzinfo=timezone.utc)


def test_calendar_month_addition_clamps_end_of_month():
    leap_day = datetime(2024, 1, 31, 12, 0, tzinfo=timezone.utc)
    assert add_calendar_months(leap_day, 1) == datetime(2024, 2, 29, 12, 0, tzinfo=timezone.utc)
    assert add_calendar_months(leap_day, 12) == datetime(2025, 1, 31, 12, 0, tzinfo=timezone.utc)
