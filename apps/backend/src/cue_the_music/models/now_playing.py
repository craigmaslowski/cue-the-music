"""NowPlaying model — singleton row tracking the currently playing album."""

from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cue_the_music.models.base import Base


class NowPlaying(Base):
    """Singleton row (id=1) representing the currently playing album."""

    __tablename__ = "now_playing"

    __table_args__ = (
        CheckConstraint("id = 1", name="ck_now_playing_singleton"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    album_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("albums.id", ondelete="RESTRICT"),
    )
    promoted_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )

    album: Mapped["Album"] = relationship(  # noqa: F821
        "Album",
        lazy="joined",
    )
