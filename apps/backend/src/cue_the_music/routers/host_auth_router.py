"""Host PIN verification endpoint.

Allows the host to authenticate with a 4-digit PIN and receive a session token.
This endpoint is intentionally NOT protected by host auth (it's how you get the token).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from cue_the_music.config import Settings, get_settings
from cue_the_music.schemas.host_auth_schemas import (
    HostPinVerifyRequest,
    HostPinVerifyResponse,
)
from cue_the_music.services.host_auth_service import (
    HostAuthService,
    get_host_auth_service,
)

router = APIRouter(prefix="/api/host", tags=["host-auth"])


@router.post("/verify-pin", response_model=HostPinVerifyResponse)
async def verify_pin(
    body: HostPinVerifyRequest,
    request: Request,
    service: Annotated[HostAuthService, Depends(get_host_auth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> HostPinVerifyResponse:
    """Verify the host PIN and return a session token.

    Rate limited to 5 attempts per IP per 60 seconds with a deliberate
    500ms delay on every attempt. Only one active host session at a time.
    """
    client_ip = request.client.host  # type: ignore[union-attr]
    token = await service.verify_pin(body.pin, client_ip, settings)
    return HostPinVerifyResponse(token=token)
