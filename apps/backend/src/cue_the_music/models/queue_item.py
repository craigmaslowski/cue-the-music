"""QueueItem model — represents an album requested for the queue."""

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cue_the_music.models.base import Base, TimestampMixin


class QueueItem(TimestampMixin, Base):
    """A queued album request from a guest."""

    __tablename__ = "queue_items"

    __table_args__ = (
        Index("idx_queue_item_album_id", "album_id"),
        Index("idx_queue_item_requested_by_ip", "requested_by_ip"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    album_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("albums.id", ondelete="RESTRICT"),
        unique=True,
    )
    requested_by_ip: Mapped[str] = mapped_column(String(45))

    album: Mapped["Album"] = relationship(  # noqa: F821
        "Album",
        lazy="joined",
    )
    votes: Mapped[list["Vote"]] = relationship(  # noqa: F821
        "Vote",
        back_populates="queue_item",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
