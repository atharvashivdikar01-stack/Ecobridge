from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.exceptions import AppException, UnauthorizedError
from ..core.logging import get_logger
from ..core.security import create_access_token, create_refresh_token, decode_token
from ..models.user import User
from ..models.collector import CollectorProfile
from ..schemas.auth import TokenResponse, UserSummary
from .otp_service import otp_service

logger = get_logger("ecobridge.auth_service")


class AuthService:
    """Manages collector authentication, registration, and token lifecycle."""

    async def authenticate_collector(
        self,
        db: AsyncSession,
        phone: str,
        otp: str,
        full_name: Optional[str] = None,
        collector_type: str = "INDIVIDUAL_PICKER",
        preferred_language: str = "en",
    ) -> TokenResponse:
        # 1. Verify OTP
        is_valid_otp = otp_service.verify_otp(phone=phone, otp=otp)
        if not is_valid_otp:
            raise AppException(
                code="INVALID_OTP",
                message="The provided OTP code is invalid or has expired.",
                status_code=400,
            )

        # 2. Check if user already exists
        result = await db.execute(select(User).where(User.phone == phone))
        user = result.scalar_one_or_none()

        if user is None:
            # Auto-register new collector (Zero-Barrier UX)
            display_name = full_name.strip() if full_name and full_name.strip() else f"Collector {phone[-4:]}"
            logger.info(f"Auto-registering new collector: phone={phone}, name={display_name}")

            user = User(
                phone=phone,
                full_name=display_name,
                role="COLLECTOR",
                status="ACTIVE",
                preferred_language=preferred_language or "en",
            )
            db.add(user)
            await db.flush()

            # Create Collector Profile
            profile = CollectorProfile(
                user_id=user.id,
                collector_type=collector_type or "INDIVIDUAL_PICKER",
            )
            db.add(profile)
            await db.commit()
            await db.refresh(user)
        else:
            # Check account status
            if user.status != "ACTIVE":
                raise AppException(
                    code="ACCOUNT_INACTIVE",
                    message=f"Your account status is {user.status}. Please contact platform support.",
                    status_code=403,
                )

            # Ensure profile exists if user is a collector and created through another flow
            if user.role == "COLLECTOR" and user.collector_profile is None:
                profile = CollectorProfile(
                    user_id=user.id,
                    collector_type=collector_type or "INDIVIDUAL_PICKER",
                )
                db.add(profile)
                await db.commit()
                await db.refresh(user)

        # 3. Generate tokens
        access_token = create_access_token(
            subject=str(user.id),
            role=user.role,
            extra_claims={"phone": user.phone, "name": user.full_name},
        )
        refresh_token = create_refresh_token(subject=str(user.id))

        user_summary = UserSummary(
            id=str(user.id),
            phone=user.phone,
            full_name=user.full_name,
            role=user.role,
            status=user.status,
            preferred_language=user.preferred_language,
            avatar_url=user.avatar_url,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_summary,
        )

    async def refresh_tokens(self, db: AsyncSession, refresh_token: str) -> TokenResponse:
        """Issues a new access token using a valid refresh token."""
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedError(
                message="Invalid token type. Expected refresh token.",
                details={"token_type": payload.get("type")},
            )

        user_id = payload.get("sub")
        import uuid
        try:
            parsed_id = uuid.UUID(str(user_id))
        except (ValueError, TypeError):
            raise UnauthorizedError(message="Malformed token: invalid subject UUID")

        result = await db.execute(select(User).where(User.id == parsed_id))
        user = result.scalar_one_or_none()

        if not user or user.status != "ACTIVE":
            raise UnauthorizedError(message="User not found or account is inactive")

        new_access_token = create_access_token(
            subject=str(user.id),
            role=user.role,
            extra_claims={"phone": user.phone, "name": user.full_name},
        )
        new_refresh_token = create_refresh_token(subject=str(user.id))

        user_summary = UserSummary(
            id=str(user.id),
            phone=user.phone,
            full_name=user.full_name,
            role=user.role,
            status=user.status,
            preferred_language=user.preferred_language,
            avatar_url=user.avatar_url,
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_summary,
        )

    async def demo_login(self, db: AsyncSession, target_role: str) -> TokenResponse:
        """Convenient zero-barrier login for competition demonstrations.
        Switches between Verified Recycler, Unverified Recycler, and Collector.
        """
        role_key = (target_role or "VERIFIED_RECYCLER").upper()

        if role_key in ("VERIFIED_RECYCLER", "RECYCLER_VERIFIED", "RECYCLER"):
            phone = "+919811111111"
            name = "Ravi Patel (EcoGreen Recyclers)"
            user_role = "RECYCLER_ADMIN"
        elif role_key in ("UNVERIFIED_RECYCLER", "PENDING_RECYCLER"):
            phone = "+919822222222"
            name = "Vikram Shah (Pending Scrap Co.)"
            user_role = "RECYCLER_ADMIN"
        else:
            phone = "+919800000001"
            name = "Raju Shinde (Verified Collector)"
            user_role = "COLLECTOR"

        result = await db.execute(select(User).where(User.phone == phone))
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                phone=phone,
                full_name=name,
                role=user_role,
                status="ACTIVE",
                preferred_language="en",
            )
            db.add(user)
            await db.flush()

            if user_role == "COLLECTOR":
                profile = CollectorProfile(
                    user_id=user.id,
                    collector_type="INDIVIDUAL_PICKER",
                )
                db.add(profile)
            await db.commit()
            await db.refresh(user)

        access_token = create_access_token(
            subject=str(user.id),
            role=user.role,
            extra_claims={"phone": user.phone, "name": user.full_name},
        )
        refresh_token = create_refresh_token(subject=str(user.id))

        user_summary = UserSummary(
            id=str(user.id),
            phone=user.phone,
            full_name=user.full_name,
            role=user.role,
            status=user.status,
            preferred_language=user.preferred_language,
            avatar_url=user.avatar_url,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_summary,
        )


auth_service = AuthService()
