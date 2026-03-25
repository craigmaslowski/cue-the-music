"""Service layer for host PIN verification and token management.

Handles rate limiting, PIN comparison, and in-memory token storage.
Only one active host session at a time — new verification overwrites old token.
Server restart clears all tokens (acceptable for local network use).
"""

import asyncio
import secrets
import time
from datetime import UTC, datetime

from cue_the_music.config import Settings
from cue_the_music.exceptions.exceptions import InvalidHostPinError
from cue_the_music.exceptions.rate_limit import PinRateLimitExceededError

# Rate limit: max attempts per IP within the time window
_MAX_ATTEMPTS = 5
_WINDOW_SECONDS = 60

# Token expires after 4 hours
_TOKEN_EXPIRY_SECONDS = 4 * 60 * 60

# Deliberate delay on every PIN attempt to make brute force impractical
_ATTEMPT_DELAY_SECONDS = 0.5


class HostTokenInfo:
    """In-memory record of an active host session token."""

    def __init__(self, created_at: datetime, ip: str) -> None:
        self.created_at = created_at
        self.ip = ip


class HostAuthService:
    """Manages host PIN verification, rate limiting, and token lifecycle.

    All state is held in-memory. A single active host token is maintained;
    new verification overwrites any previous token.
    """

    def __init__(self) -> None:
        # Rate-limit tracking: IP -> list of attempt timestamps
        self._attempts: dict[str, list[float]] = {}

        # Single active host token (last-verify-wins)
        self._active_token: str | None = None
        self._token_info: HostTokenInfo | None = None

    def _prune_attempts(self, ip: str) -> list[float]:
        """Remove expired attempts outside the rate-limit window for an IP."""
        now = time.monotonic()
        cutoff = now - _WINDOW_SECONDS
        timestamps = self._attempts.get(ip, [])
        valid = [ts for ts in timestamps if ts > cutoff]
        self._attempts[ip] = valid
        return valid

    def _check_rate_limit(self, ip: str) -> None:
        """Raise PinRateLimitExceededError if the IP has exceeded the attempt limit."""
        recent = self._prune_attempts(ip)
        if len(recent) >= _MAX_ATTEMPTS:
            raise PinRateLimitExceededError()

    def _record_attempt(self, ip: str) -> None:
        """Record a PIN verification attempt for rate-limiting purposes."""
        now = time.monotonic()
        if ip not in self._attempts:
            self._attempts[ip] = []
        self._attempts[ip].append(now)

    async def verify_pin(self, pin: str, ip: str, settings: Settings) -> str:
        """Verify the host PIN and return a session token.

        Applies rate limiting and a deliberate delay on every attempt.
        On success, generates a new token and invalidates any previous session.
        """
        self._check_rate_limit(ip)
        self._record_attempt(ip)

        # Deliberate delay to throttle brute-force attempts
        await asyncio.sleep(_ATTEMPT_DELAY_SECONDS)

        if pin != settings.HOST_PIN:
            raise InvalidHostPinError()

        # Generate new token and overwrite any existing session
        token = secrets.token_urlsafe(32)
        self._active_token = token
        self._token_info = HostTokenInfo(
            created_at=datetime.now(tz=UTC),
            ip=ip,
        )

        return token

    def validate_token(self, token: str) -> bool:
        """Check whether a token is the active host token and not expired."""
        if self._active_token is None or self._token_info is None:
            return False

        if token != self._active_token:
            return False

        # Check expiry
        age = (
            datetime.now(tz=UTC) - self._token_info.created_at
        ).total_seconds()
        if age > _TOKEN_EXPIRY_SECONDS:
            # Token expired — clear it
            self._active_token = None
            self._token_info = None
            return False

        return True


# Module-level singleton used by the FastAPI dependency
_host_auth_service: HostAuthService | None = None


def get_host_auth_service() -> HostAuthService:
    """Return the singleton HostAuthService instance (created on first call)."""
    global _host_auth_service  # noqa: PLW0603
    if _host_auth_service is None:
        _host_auth_service = HostAuthService()
    return _host_auth_service
