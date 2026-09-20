from typing import Annotated, Optional
from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.exceptions import ForbiddenError, UnauthorizedError
from ..core.security import decode_token
from ..models.user import User


async def get_current_user(
    authorization: Annotated[Optional[str], Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency extracting and validating the authenticated User from the Bearer token."""
    if not authorization:
        raise UnauthorizedError(message="Authorization header missing")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedError(message="Invalid authorization format. Expected 'Bearer <token>'")

    token = parts[1]
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise UnauthorizedError(
            message="Invalid token type. Expected access token",
            details={"token_type": payload.get("type")},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError(message="Malformed token: missing subject claim")

    import uuid
    try:
        parsed_id = uuid.UUID(str(user_id))
    except (ValueError, TypeError):
        raise UnauthorizedError(message="Malformed token: invalid subject UUID")

    result = await db.execute(select(User).where(User.id == parsed_id))
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedError(message="User not found")

    if user.status != "ACTIVE":
        raise UnauthorizedError(message=f"User account is {user.status}")

    return user


async def get_current_collector(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency verifying that the current user has the COLLECTOR role."""
    if current_user.role != "COLLECTOR":
        raise ForbiddenError(
            message="Access restricted to informal collectors",
            details={"current_role": current_user.role},
        )
    return current_user


async def get_current_recycler(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency verifying that the current user has a RECYCLER role."""
    if current_user.role not in ("RECYCLER_ADMIN", "RECYCLER_OPERATOR", "PLATFORM_ADMIN"):
        raise ForbiddenError(
            message="Access restricted to certified recyclers",
            details={"current_role": current_user.role},
        )
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency verifying that the current user has the PLATFORM_ADMIN role."""
    if current_user.role != "PLATFORM_ADMIN":
        raise ForbiddenError(
            message="Access restricted to platform administrators",
            details={"current_role": current_user.role},
        )
    return current_user

