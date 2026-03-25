"""Vote model — represents a guest's vote on a queue item."""

from sqlalchemy import ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cue_the_music.models.base import Base, TimestampMixin


class Vote(TimestampMixin, Base):
    """A vote (up or down) on a queue item, one per IP per queue item."""

    __tablename__ = "votes"

    __table_args__ = (
        UniqueConstraint("queue_item_id", "voter_ip", name="uq_vote_queue_item_voter"),
        Index("idx_vote_queue_item_id", "queue_item_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    queue_item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("queue_items.id", ondelete="CASCADE"),
    )
    voter_ip: Mapped[str] = mapped_column(String(45))
    value: Mapped[int] = mapped_column(Integer)

    queue_item: Mapped["QueueItem"] = relationship(  # noqa: F821
        "QueueItem",
        back_populates="votes",
    )
