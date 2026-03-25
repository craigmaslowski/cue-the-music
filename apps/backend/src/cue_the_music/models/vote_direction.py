"""VoteDirection enum for queue item voting."""

from enum import IntEnum


class VoteDirection(IntEnum):
    """Direction of a vote on a queue item."""

    DOWN = -1
    UP = 1
