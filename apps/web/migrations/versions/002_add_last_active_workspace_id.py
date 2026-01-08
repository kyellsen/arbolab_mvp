"""Add last active workspace reference to user

Revision ID: 002_add_last_active_workspace_id
Revises: 001_add_user_profile_fields
Create Date: 2026-01-08

Adds User.last_active_workspace_id for persisted workspace selection.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "002_add_last_active_workspace_id"
down_revision: Union[str, None] = "001_add_user_profile_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _workspace_id_type() -> sa.types.TypeEngine:
    bind = op.get_bind()
    if bind and bind.dialect.name == "postgresql":
        return postgresql.UUID(as_uuid=True)
    return sa.String(length=36)


def upgrade() -> None:
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "last_active_workspace_id",
                _workspace_id_type(),
                sa.ForeignKey("workspace.id"),
                nullable=True,
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_column("last_active_workspace_id")
