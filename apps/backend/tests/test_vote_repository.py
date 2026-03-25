"""Tests for the VoteRepository — database query layer."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from cue_the_music.models.album import Album
from cue_the_music.models.vote import Vote
from cue_the_music.models.vote_direction import VoteDirection
from cue_the_music.repositories.queue_repository import QueueRepository
from cue_the_music.repositories.vote_repository import VoteRepository


async def _seed_queue_item(session: AsyncSession, release_id: str = "1001") -> int:
    """Seed an album and queue item, return the queue_item_id."""
    album = Album(
        artist="Test Artist",
        cover_art_thumbnail_url="https://example.com/thumb.jpg",
        cover_art_url="https://example.com/cover.jpg",
        discogs_release_id=release_id,
        genre_tags=["Rock"],
        label="Test Label",
        style_tags=["Punk"],
        title="Test Album",
        year=1977,
    )
    session.add(album)
    await session.flush()

    queue_repo = QueueRepository(session)
    item = await queue_repo.add_to_queue(album.id, "192.168.1.10")
    return item.id


@pytest.mark.asyncio
class TestVoteRepositoryUpsert:
    """Tests for VoteRepository.upsert_vote()."""

    async def test_inserts_new_vote(self, async_session: AsyncSession) -> None:
        qi_id = await _seed_queue_item(async_session, "v001")
        repo = VoteRepository(async_session)

        await repo.upsert_vote(qi_id, "192.168.1.20", VoteDirection.UP)
        await async_session.flush()

        # Verify via direct query
        from sqlalchemy import select

        stmt = select(Vote).where(Vote.queue_item_id == qi_id)
        result = await async_session.execute(stmt)
        vote = result.scalar_one()
        assert vote.value == VoteDirection.UP
        assert vote.voter_ip == "192.168.1.20"

    async def test_updates_existing_vote(self, async_session: AsyncSession) -> None:
        qi_id = await _seed_queue_item(async_session, "v002")
        repo = VoteRepository(async_session)

        await repo.upsert_vote(qi_id, "192.168.1.20", VoteDirection.UP)
        await async_session.flush()
        await repo.upsert_vote(qi_id, "192.168.1.20", VoteDirection.DOWN)
        await async_session.flush()

        from sqlalchemy import func, select

        stmt = select(func.count()).select_from(Vote).where(
            Vote.queue_item_id == qi_id
        )
        result = await async_session.execute(stmt)
        assert result.scalar_one() == 1

        stmt2 = select(Vote).where(Vote.queue_item_id == qi_id)
        result2 = await async_session.execute(stmt2)
        vote = result2.scalar_one()
        assert vote.value == VoteDirection.DOWN


@pytest.mark.asyncio
class TestVoteRepositoryRemove:
    """Tests for VoteRepository.remove_vote()."""

    async def test_removes_existing_vote(self, async_session: AsyncSession) -> None:
        qi_id = await _seed_queue_item(async_session, "v003")
        repo = VoteRepository(async_session)

        await repo.upsert_vote(qi_id, "192.168.1.20", VoteDirection.UP)
        await async_session.flush()

        removed = await repo.remove_vote(qi_id, "192.168.1.20")
        assert removed is True

    async def test_returns_false_for_nonexistent(
        self, async_session: AsyncSession
    ) -> None:
        qi_id = await _seed_queue_item(async_session, "v004")
        repo = VoteRepository(async_session)

        removed = await repo.remove_vote(qi_id, "192.168.1.99")
        assert removed is False


@pytest.mark.asyncio
class TestVoteAggregates:
    """Tests for vote aggregation via QueueRepository."""

    async def test_aggregates_vote_counts(
        self, async_session: AsyncSession
    ) -> None:
        qi_id = await _seed_queue_item(async_session, "v005")
        vote_repo = VoteRepository(async_session)
        queue_repo = QueueRepository(async_session)

        await vote_repo.upsert_vote(qi_id, "192.168.1.20", VoteDirection.UP)
        await vote_repo.upsert_vote(qi_id, "192.168.1.21", VoteDirection.UP)
        await vote_repo.upsert_vote(qi_id, "192.168.1.22", VoteDirection.DOWN)
        await async_session.flush()

        aggregates = await queue_repo.get_vote_aggregates(
            [qi_id], "192.168.1.20"
        )

        assert aggregates[qi_id]["up_count"] == 2
        assert aggregates[qi_id]["down_count"] == 1
        assert aggregates[qi_id]["my_vote"] == VoteDirection.UP

    async def test_no_votes_returns_zeros(
        self, async_session: AsyncSession
    ) -> None:
        qi_id = await _seed_queue_item(async_session, "v006")
        queue_repo = QueueRepository(async_session)

        aggregates = await queue_repo.get_vote_aggregates(
            [qi_id], "192.168.1.20"
        )

        assert aggregates[qi_id]["up_count"] == 0
        assert aggregates[qi_id]["down_count"] == 0
        assert aggregates[qi_id]["my_vote"] is None
