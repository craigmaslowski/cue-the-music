"""create_queue_vote_now_playing_tables

Revision ID: a3b7c9d1e2f4
Revises: 12d5748fc624
Create Date: 2026-03-25 18:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a3b7c9d1e2f4"
down_revision: Union[str, Sequence[str], None] = "12d5748fc624"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create queue_items, votes, and now_playing tables."""
    # Queue items table
    op.create_table(
        "queue_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("album_id", sa.Integer(), nullable=False),
        sa.Column("requested_by_ip", sa.String(length=45), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["album_id"],
            ["albums.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("album_id"),
    )
    op.create_index("idx_queue_item_album_id", "queue_items", ["album_id"])
    op.create_index(
        "idx_queue_item_requested_by_ip", "queue_items", ["requested_by_ip"]
    )

    # Votes table
    op.create_table(
        "votes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("queue_item_id", sa.Integer(), nullable=False),
        sa.Column("voter_ip", sa.String(length=45), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["queue_item_id"],
            ["queue_items.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "queue_item_id", "voter_ip", name="uq_vote_queue_item_voter"
        ),
    )
    op.create_index("idx_vote_queue_item_id", "votes", ["queue_item_id"])

    # Now playing table (singleton: CHECK id = 1)
    op.create_table(
        "now_playing",
        sa.Column("id", sa.Integer(), nullable=False, default=1),
        sa.Column("album_id", sa.Integer(), nullable=False),
        sa.Column(
            "promoted_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.CheckConstraint("id = 1", name="ck_now_playing_singleton"),
        sa.ForeignKeyConstraint(
            ["album_id"],
            ["albums.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Drop queue_items, votes, and now_playing tables."""
    op.drop_table("now_playing")
    op.drop_index("idx_vote_queue_item_id", table_name="votes")
    op.drop_table("votes")
    op.drop_index("idx_queue_item_requested_by_ip", table_name="queue_items")
    op.drop_index("idx_queue_item_album_id", table_name="queue_items")
    op.drop_table("queue_items")
