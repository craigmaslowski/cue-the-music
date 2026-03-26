"""Album model — represents a vinyl record from the host's Discogs collection."""


from sqlalchemy import JSON, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from cue_the_music.models.base import Base, TimestampMixin


class Album(TimestampMixin, Base):
    """A vinyl album synced from the host's Discogs collection."""

    __tablename__ = "albums"

    # Indexes defined at the table level for search performance
    __table_args__ = (
        Index("idx_album_artist", "artist"),
        Index("idx_album_title", "title"),
        Index("idx_album_year", "year"),
    )

    artist: Mapped[str] = mapped_column(String(500))
    cover_art_thumbnail_url: Mapped[str | None] = mapped_column(Text)
    cover_art_url: Mapped[str | None] = mapped_column(Text)
    discogs_master_id: Mapped[int | None] = mapped_column(Integer)
    discogs_release_id: Mapped[str] = mapped_column(
        String(50), unique=True, index=True
    )
    genre_tags: Mapped[list | None] = mapped_column(JSON, default=list)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    label: Mapped[str | None] = mapped_column(String(500))
    style_tags: Mapped[list | None] = mapped_column(JSON, default=list)
    title: Mapped[str] = mapped_column(String(500))
    tracklist: Mapped[list | None] = mapped_column(JSON, nullable=True)
    year: Mapped[int | None] = mapped_column(Integer)
