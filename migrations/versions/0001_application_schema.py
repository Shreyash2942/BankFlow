"""Create the application schema; domain tables follow in Day 3.

Revision ID: 0001
Revises: None
"""

from alembic import op
from sqlalchemy.schema import CreateSchema, DropSchema

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute(CreateSchema("bankflow"))


def downgrade():
    # No CASCADE: unexpected objects must prevent a destructive rollback.
    op.execute(DropSchema("bankflow"))
