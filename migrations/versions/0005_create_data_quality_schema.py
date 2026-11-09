"""create data quality result store

Revision ID: 0005
Revises: 0004
"""

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

SCHEMA = "bankflow_quality"


def upgrade():
    op.execute(sa.schema.CreateSchema(SCHEMA))
    op.create_table(
        "quality_runs",
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("triggered_by", sa.String(length=64), nullable=False),
        sa.Column("total_rules", sa.Integer(), nullable=False),
        sa.Column("passed_rules", sa.Integer(), nullable=False),
        sa.Column("failed_rules", sa.Integer(), nullable=False),
        sa.Column("error_rules", sa.Integer(), nullable=False),
        sa.Column("total_violations", sa.BigInteger(), nullable=False),
        sa.CheckConstraint("status IN ('passed', 'failed', 'error')", name="ck_quality_run_status"),
        sa.CheckConstraint(
            "total_rules = passed_rules + failed_rules + error_rules",
            name="ck_quality_run_rule_totals",
        ),
        sa.PrimaryKeyConstraint("run_id", name="pk_quality_runs"),
        schema=SCHEMA,
    )
    op.create_table(
        "quality_results",
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("rule_id", sa.String(length=96), nullable=False),
        sa.Column("layer", sa.String(length=24), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("description", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("violation_count", sa.BigInteger(), nullable=False),
        sa.Column("message", sa.String(length=240), nullable=True),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('passed', 'failed', 'error')", name="ck_quality_result_status"
        ),
        sa.CheckConstraint("violation_count >= 0", name="ck_quality_result_nonnegative_violations"),
        sa.ForeignKeyConstraint(
            ["run_id"],
            [f"{SCHEMA}.quality_runs.run_id"],
            name="fk_quality_results_run",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("run_id", "rule_id", name="pk_quality_results"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_quality_runs_completed_at",
        "quality_runs",
        ["completed_at"],
        schema=SCHEMA,
    )


def downgrade():
    op.drop_index("ix_quality_runs_completed_at", table_name="quality_runs", schema=SCHEMA)
    op.drop_table("quality_results", schema=SCHEMA)
    op.drop_table("quality_runs", schema=SCHEMA)
    op.execute(sa.schema.DropSchema(SCHEMA))
