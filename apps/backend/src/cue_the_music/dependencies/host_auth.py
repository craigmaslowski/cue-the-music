"""Host authentication dependency for protecting host-only endpoints.

Reads the X-Host-Token header and validates it against the active host session.
"""

from typing import Annotated

from fastapi import Depends, Header

from cue_the_music.exceptions.exceptions import UnauthorizedHostActionError
from cue_the_music.services.host_auth_service import (
    HostAuthService,
    get_host_auth_service,
)


async def require_host_token(
    host_auth_service: Annotated[HostAuthService, Depends(get_host_auth_service)],
    x_host_token: Annotated[str | None, Header()] = None,
) -> None:
    """Validate the X-Host-Token header against the active host session.

    Raises UnauthorizedHostActionError (403) if the token is missing,
    invalid, or expired.
    """
    if x_host_token is None:
        raise UnauthorizedHostActionError()

    if not host_auth_service.validate_token(x_host_token):
        raise UnauthorizedHostActionError()


# Annotated alias for use in router Depends() declarations
HostAuthDep = Annotated[None, Depends(require_host_token)]
