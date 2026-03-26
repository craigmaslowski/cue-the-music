"""Dependency for injecting the SSE broadcaster from app.state."""

from fastapi import Request

from cue_the_music.events.broadcaster import MessageBroadcaster


def get_broadcaster(request: Request) -> MessageBroadcaster:
    """Retrieve the MessageBroadcaster singleton from app.state.

    The broadcaster is created during the application lifespan startup
    and stored on app.state.broadcaster.
    """
    return request.app.state.broadcaster  # type: ignore[no-any-return]
