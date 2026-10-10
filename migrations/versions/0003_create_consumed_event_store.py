"""create consumed event store

Revision ID: 0003
Revises: 0002
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "consumed_events",
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("schema_version", sa.SmallInteger(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("topic", sa.String(length=249), nullable=False),
        sa.Column("partition", sa.Integer(), nullable=False),
        sa.Column("offset", sa.BigInteger(), nullable=False),
        sa.Column("consumer_group", sa.String(length=255), nullable=False),
        sa.Column(
            "consumed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("event_id", name=op.f("pk_consumed_events")),
        sa.UniqueConstraint(
            "topic",
            "partition",
            "offset",
            name="uq_consumed_events_kafka_position",
        ),
        schema="bankflow",
    )
    op.create_index(
        "ix_consumed_events_consumed_at",
        "consumed_events",
        ["consumed_at"],
        unique=False,
        schema="bankflow",
    )
    op.create_index(
        "ix_consumed_events_type_occurred_at",
        "consumed_events",
        ["event_type", "occurred_at"],
        unique=False,
        schema="bankflow",
    )


def downgrade():
    op.drop_index(
        "ix_consumed_events_type_occurred_at",
        table_name="consumed_events",
        schema="bankflow",
    )
    op.drop_index(
        "ix_consumed_events_consumed_at",
        table_name="consumed_events",
        schema="bankflow",
    )
    op.drop_table("consumed_events", schema="bankflow")
