"""add_discogs_master_id_to_albums

Revision ID: b4c8d2e5f7a1
Revises: a3b7c9d1e2f4
Create Date: 2026-03-25 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4c8d2e5f7a1'
down_revision: Union[str, Sequence[str]] = 'a3b7c9d1e2f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add discogs_master_id column to albums table."""
    op.add_column('albums', sa.Column('discogs_master_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Remove discogs_master_id column from albums table."""
    op.drop_column('albums', 'discogs_master_id')
