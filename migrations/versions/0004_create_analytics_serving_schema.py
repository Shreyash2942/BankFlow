"""create analytics serving schema

Revision ID: 0004
Revises: 0003
"""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

SCHEMA = "bankflow_serving"


def _audit_columns() -> tuple[sa.Column, sa.Column]:
    return (
        sa.Column("source_gold_processed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "loaded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def upgrade():
    op.execute(sa.schema.CreateSchema(SCHEMA))
    op.create_table(
        "analytics_daily_transactions",
        sa.Column("metric_date", sa.Date(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("transaction_event_count", sa.BigInteger(), nullable=False),
        sa.Column("monetary_attempt_count", sa.BigInteger(), nullable=False),
        sa.Column("successful_transaction_count", sa.BigInteger(), nullable=False),
        sa.Column("declined_transaction_count", sa.BigInteger(), nullable=False),
        sa.Column("balance_inquiry_count", sa.BigInteger(), nullable=False),
        sa.Column("deposit_count", sa.BigInteger(), nullable=False),
        sa.Column("successful_withdrawal_count", sa.BigInteger(), nullable=False),
        sa.Column("declined_withdrawal_count", sa.BigInteger(), nullable=False),
        sa.Column("total_deposit_amount", sa.Numeric(38, 2), nullable=False),
        sa.Column("total_withdrawal_amount", sa.Numeric(38, 2), nullable=False),
        sa.Column("total_declined_amount", sa.Numeric(38, 2), nullable=False),
        sa.Column("average_transaction_value", sa.Numeric(38, 2), nullable=False),
        sa.Column("success_rate", sa.Numeric(9, 6), nullable=False),
        sa.Column("decline_rate", sa.Numeric(9, 6), nullable=False),
        sa.Column("unique_account_count", sa.BigInteger(), nullable=False),
        sa.Column("first_event_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_event_at", sa.DateTime(timezone=True), nullable=False),
        *_audit_columns(),
        sa.CheckConstraint(
            "currency = upper(currency) AND char_length(currency) = 3",
            name="ck_daily_currency_iso_style",
        ),
        sa.CheckConstraint(
            "monetary_attempt_count = successful_transaction_count + declined_transaction_count",
            name="ck_daily_attempt_reconciliation",
        ),
        sa.CheckConstraint(
            "success_rate BETWEEN 0 AND 1 AND decline_rate BETWEEN 0 AND 1",
            name="ck_daily_rate_bounds",
        ),
        sa.PrimaryKeyConstraint("metric_date", "currency", name="pk_serving_daily"),
        schema=SCHEMA,
    )
    op.create_table(
        "analytics_authentication_metrics",
        sa.Column("metric_date", sa.Date(), nullable=False),
        sa.Column("authentication_event_count", sa.BigInteger(), nullable=False),
        sa.Column("authentication_attempt_count", sa.BigInteger(), nullable=False),
        sa.Column("successful_authentication_count", sa.BigInteger(), nullable=False),
        sa.Column("failed_authentication_count", sa.BigInteger(), nullable=False),
        sa.Column("card_lockout_count", sa.BigInteger(), nullable=False),
        sa.Column("session_end_count", sa.BigInteger(), nullable=False),
        sa.Column("known_subject_event_count", sa.BigInteger(), nullable=False),
        sa.Column("unknown_subject_event_count", sa.BigInteger(), nullable=False),
        sa.Column("unique_account_count", sa.BigInteger(), nullable=False),
        sa.Column("unique_card_count", sa.BigInteger(), nullable=False),
        sa.Column("success_rate", sa.Numeric(9, 6), nullable=False),
        sa.Column("failure_rate", sa.Numeric(9, 6), nullable=False),
        sa.Column("first_event_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_event_at", sa.DateTime(timezone=True), nullable=False),
        *_audit_columns(),
        sa.CheckConstraint(
            "authentication_attempt_count = successful_authentication_count + "
            "failed_authentication_count + card_lockout_count",
            name="ck_auth_attempt_reconciliation",
        ),
        sa.CheckConstraint(
            "authentication_event_count = authentication_attempt_count + session_end_count",
            name="ck_auth_event_reconciliation",
        ),
        sa.CheckConstraint(
            "success_rate BETWEEN 0 AND 1 AND failure_rate BETWEEN 0 AND 1",
            name="ck_auth_rate_bounds",
        ),
        sa.PrimaryKeyConstraint("metric_date", name="pk_serving_authentication"),
        schema=SCHEMA,
    )
    op.create_table(
        "analytics_account_activity",
        sa.Column("metric_date", sa.Date(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("activity_event_count", sa.BigInteger(), nullable=False),
        sa.Column("transaction_event_count", sa.BigInteger(), nullable=False),
        sa.Column("distinct_transaction_count", sa.BigInteger(), nullable=False),
        sa.Column("completed_monetary_transaction_count", sa.BigInteger(), nullable=False),
        sa.Column("declined_transaction_count", sa.BigInteger(), nullable=False),
        sa.Column("balance_inquiry_count", sa.BigInteger(), nullable=False),
        sa.Column("deposit_count", sa.BigInteger(), nullable=False),
        sa.Column("successful_withdrawal_count", sa.BigInteger(), nullable=False),
        sa.Column("closure_event_count", sa.BigInteger(), nullable=False),
        sa.Column("total_deposit_amount", sa.Numeric(38, 2), nullable=False),
        sa.Column("total_withdrawal_amount", sa.Numeric(38, 2), nullable=False),
        sa.Column("total_declined_amount", sa.Numeric(38, 2), nullable=False),
        sa.Column("opening_balance", sa.Numeric(18, 2), nullable=False),
        sa.Column("closing_balance", sa.Numeric(18, 2), nullable=False),
        sa.Column("account_status", sa.String(length=32), nullable=False),
        sa.Column("account_closed", sa.Boolean(), nullable=False),
        sa.Column("first_activity_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=False),
        *_audit_columns(),
        sa.CheckConstraint(
            "currency = upper(currency) AND char_length(currency) = 3",
            name="ck_account_currency_iso_style",
        ),
        sa.CheckConstraint(
            "activity_event_count = transaction_event_count + closure_event_count",
            name="ck_account_activity_reconciliation",
        ),
        sa.PrimaryKeyConstraint(
            "metric_date", "account_id", "currency", name="pk_serving_account_activity"
        ),
        schema=SCHEMA,
    )
    op.create_table(
        "analytics_hourly_volume",
        sa.Column("event_hour", sa.DateTime(timezone=True), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("transaction_type", sa.String(length=32), nullable=False),
        sa.Column("transaction_status", sa.String(length=32), nullable=False),
        sa.Column("transaction_event_count", sa.BigInteger(), nullable=False),
        sa.Column("total_transaction_amount", sa.Numeric(38, 2), nullable=False),
        sa.Column("average_transaction_amount", sa.Numeric(38, 2), nullable=False),
        sa.Column("unique_account_count", sa.BigInteger(), nullable=False),
        sa.Column("first_event_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_event_at", sa.DateTime(timezone=True), nullable=False),
        *_audit_columns(),
        sa.CheckConstraint(
            "currency = upper(currency) AND char_length(currency) = 3",
            name="ck_hourly_currency_iso_style",
        ),
        sa.CheckConstraint("transaction_event_count > 0", name="ck_hourly_nonempty"),
        sa.PrimaryKeyConstraint(
            "event_hour",
            "currency",
            "transaction_type",
            "transaction_status",
            name="pk_serving_hourly_volume",
        ),
        schema=SCHEMA,
    )


def downgrade():
    op.drop_table("analytics_hourly_volume", schema=SCHEMA)
    op.drop_table("analytics_account_activity", schema=SCHEMA)
    op.drop_table("analytics_authentication_metrics", schema=SCHEMA)
    op.drop_table("analytics_daily_transactions", schema=SCHEMA)
    op.execute(sa.schema.DropSchema(SCHEMA))
