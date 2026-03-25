"""Pydantic schemas for host PIN verification."""

from pydantic import BaseModel, Field


class HostPinVerifyRequest(BaseModel):
    """Request to verify a host PIN."""

    pin: str = Field(min_length=4, max_length=4, pattern=r"^\d{4}$")


class HostPinVerifyResponse(BaseModel):
    """Response containing the host session token."""

    token: str
