"""Add user profile fields

Revision ID: 001
Revises: 
Create Date: 2026-01-08

This migration adds the missing profile fields to the User table:
- full_name
- organization
- address_line1
- address_line2
- city
- zip_code
- country
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_add_user_profile_fields'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to user table if they don't exist
    # Using batch mode for SQLite compatibility
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('full_name', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('organization', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('address_line1', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('address_line2', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('city', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('zip_code', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('country', sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('country')
        batch_op.drop_column('zip_code')
        batch_op.drop_column('city')
        batch_op.drop_column('address_line2')
        batch_op.drop_column('address_line1')
        batch_op.drop_column('organization')
        batch_op.drop_column('full_name')
