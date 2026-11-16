"""Create core licensing and audit tables."""
from alembic import op
import sqlalchemy as sa

revision="0001_licensing_tables"
down_revision=None
branch_labels=None
depends_on=None

def upgrade():
    op.create_table("devices",
        sa.Column("id",sa.String(36),primary_key=True), sa.Column("fingerprint_hash",sa.String(64),nullable=False,unique=True),
        sa.Column("token_hash",sa.String(64),nullable=False,unique=True), sa.Column("trial_started_at",sa.DateTime(timezone=True),nullable=False),
        sa.Column("subscription_expires_at",sa.DateTime(timezone=True)), sa.Column("subscription_revoked",sa.Boolean(),nullable=False,server_default=sa.false()))
    op.create_table("activation_codes",
        sa.Column("id",sa.String(36),primary_key=True), sa.Column("code_hash",sa.String(64),nullable=False,unique=True),
        sa.Column("plan",sa.String(10),nullable=False), sa.Column("issued_at",sa.DateTime(timezone=True),nullable=False),
        sa.Column("redeemed_at",sa.DateTime(timezone=True)), sa.Column("redeemed_device_id",sa.String(36),sa.ForeignKey("devices.id")),
        sa.Column("revoked_at",sa.DateTime(timezone=True)))
    op.create_table("audit_logs",sa.Column("id",sa.String(36),primary_key=True),sa.Column("action",sa.String(80),nullable=False),sa.Column("target_id",sa.String(36)),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))

def downgrade():
    op.drop_table("audit_logs"); op.drop_table("activation_codes"); op.drop_table("devices")
