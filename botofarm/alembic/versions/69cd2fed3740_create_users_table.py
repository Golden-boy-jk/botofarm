"""create users table

Revision ID: 69cd2fed3740
Revises: 
Create Date: 2025-11-20 00:45:58.295343

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '69cd2fed3740'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("login", sa.String(length=255), nullable=False, unique=True, index=True),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("env", sa.String(length=50), nullable=False),
        sa.Column("domain", sa.String(length=50), nullable=False),
        sa.Column("locktime", sa.DateTime(timezone=True), nullable=True),
    )

def downgrade() -> None:
    op.drop_table("users")