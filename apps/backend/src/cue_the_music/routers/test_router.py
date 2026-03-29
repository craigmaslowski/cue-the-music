"""Test-only API endpoint for resetting the database with seed data.

Only mounted when TEST_MODE=true. Provides a clean, predictable state
for Playwright E2E tests without touching the dev/production database.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import delete, text
from sqlalchemy.ext.asyncio import AsyncSession

from cue_the_music.dependencies.database import get_session
from cue_the_music.models.album import Album

router = APIRouter(prefix="/api/test", tags=["test"])

# Baseline seed albums for E2E tests — diverse genres, decades, tracklist states
_SEED_ALBUMS = [
    {
        "artist": "Black Sabbath",
        "cover_art_thumbnail_url": None,
        "cover_art_url": None,
        "discogs_release_id": "e2e-005",
        "genre_tags": ["Rock"],
        "label": "Vertigo",
        "style_tags": ["Heavy Metal"],
        "title": "Paranoid",
        "tracklist": None,
        "year": 1970,
    },
    {
        "artist": "Daft Punk",
        "cover_art_thumbnail_url": None,
        "cover_art_url": None,
        "discogs_release_id": "e2e-006",
        "genre_tags": ["Electronic"],
        "label": "Virgin",
        "style_tags": ["House"],
        "title": "Discovery",
        "tracklist": [
            {"duration": "5:20", "position": "1", "title": "One More Time"},
            {"duration": "3:44", "position": "2", "title": "Aerodynamic"},
        ],
        "year": 2001,
    },
    {
        "artist": "Kraftwerk",
        "cover_art_thumbnail_url": None,
        "cover_art_url": None,
        "discogs_release_id": "e2e-003",
        "genre_tags": ["Electronic"],
        "label": "Kling Klang",
        "style_tags": ["Synth-pop"],
        "title": "Trans-Europe Express",
        "tracklist": [
            {"duration": "6:36", "position": "A1", "title": "Europe Endless"},
            {"duration": "6:48", "position": "B1", "title": "Trans-Europe Express"},
        ],
        "year": 1977,
    },
    {
        "artist": "Metallica",
        "cover_art_thumbnail_url": None,
        "cover_art_url": None,
        "discogs_release_id": "e2e-004",
        "genre_tags": ["Rock", "Metal"],
        "label": "Elektra",
        "style_tags": ["Thrash"],
        "title": "Master of Puppets",
        "tracklist": None,
        "year": 1986,
    },
    {
        "artist": "Miles Davis",
        "cover_art_thumbnail_url": None,
        "cover_art_url": None,
        "discogs_release_id": "e2e-001",
        "genre_tags": ["Jazz"],
        "label": "Columbia",
        "style_tags": ["Modal"],
        "title": "Kind of Blue",
        "tracklist": [
            {"duration": "9:22", "position": "A1", "title": "So What"},
            {"duration": "9:46", "position": "A2", "title": "Freddie Freeloader"},
        ],
        "year": 1959,
    },
    {
        "artist": "The Clash",
        "cover_art_thumbnail_url": None,
        "cover_art_url": None,
        "discogs_release_id": "e2e-002",
        "genre_tags": ["Rock"],
        "label": "CBS",
        "style_tags": ["Punk"],
        "title": "London Calling",
        "tracklist": [
            {"duration": "3:20", "position": "A1", "title": "London Calling"},
            {"duration": "3:51", "position": "A2", "title": "Brand New Cadillac"},
        ],
        "year": 1979,
    },
]


@router.post("/reset")
async def reset_database(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, str]:
    """Truncate all tables, reset auth state, and seed baseline album data."""
    # Reset host auth rate limiter to prevent lockout across tests
    import cue_the_music.services.host_auth_service as auth_module

    auth_module._host_auth_service = None

    # Delete in FK order: votes -> queue_items -> now_playing -> albums
    await session.execute(text("DELETE FROM votes"))
    await session.execute(text("DELETE FROM queue_items"))
    await session.execute(text("DELETE FROM now_playing"))
    await session.execute(delete(Album))

    # Seed baseline albums
    for album_data in _SEED_ALBUMS:
        session.add(Album(**album_data))

    return {"status": "reset"}
