"""Rate-limit exception for PIN verification attempts."""


class PinRateLimitExceededError(Exception):
    """Raised when a client exceeds the PIN attempt rate limit (429)."""

    def __init__(self) -> None:
        self.message = "Too many PIN attempts. Please wait and try again."
        super().__init__(self.message)
