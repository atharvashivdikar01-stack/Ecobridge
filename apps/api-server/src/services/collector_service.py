from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import NotFoundError
from ..models.user import User
from ..models.collector import CollectorProfile
from ..schemas.collector import (
    CollectorProfileResponse,
    CollectorProfileUpdate,
    CollectorKycSubmission,
    CollectorStatsResponse,
)


class CollectorService:
    """Manages collector profile retrieval, updates, KYC, and performance metrics."""

    async def get_profile(self, db: AsyncSession, user: User) -> CollectorProfileResponse:
        """Fetches the complete profile and metrics for the given collector."""
        result = await db.execute(
            select(CollectorProfile).where(CollectorProfile.user_id == user.id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise NotFoundError(message="Collector profile not found for this account")

        return self._build_response(user, profile)

    async def update_profile(
        self,
        db: AsyncSession,
        user: User,
        update_data: CollectorProfileUpdate,
    ) -> CollectorProfileResponse:
        """Applies partial profile updates for user and payment coordinates."""
        result = await db.execute(
            select(CollectorProfile).where(CollectorProfile.user_id == user.id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise NotFoundError(message="Collector profile not found for this account")

        # Update User fields if provided
        if update_data.full_name is not None and update_data.full_name.strip():
            user.full_name = update_data.full_name.strip()
        if update_data.preferred_language is not None and update_data.preferred_language.strip():
            user.preferred_language = update_data.preferred_language.strip()

        # Update CollectorProfile fields if provided
        if update_data.upi_id is not None:
            profile.upi_id = update_data.upi_id.strip() if update_data.upi_id else None
        if update_data.bank_account_number is not None:
            profile.bank_account_number = update_data.bank_account_number.strip() if update_data.bank_account_number else None
        if update_data.ifsc_code is not None:
            profile.ifsc_code = update_data.ifsc_code.strip() if update_data.ifsc_code else None

        await db.commit()
        await db.refresh(user)
        await db.refresh(profile)

        return self._build_response(user, profile)

    async def submit_kyc(
        self,
        db: AsyncSession,
        user: User,
        kyc_data: CollectorKycSubmission,
    ) -> CollectorProfileResponse:
        """Submits national identity document for KYC verification."""
        result = await db.execute(
            select(CollectorProfile).where(CollectorProfile.user_id == user.id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise NotFoundError(message="Collector profile not found for this account")

        profile.national_id_type = kyc_data.national_id_type
        profile.national_id_number = kyc_data.national_id_number.strip()
        profile.verified_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(profile)

        return self._build_response(user, profile)

    async def get_stats(self, db: AsyncSession, user: User) -> CollectorStatsResponse:
        """Returns collection stats for the current collector."""
        result = await db.execute(
            select(CollectorProfile).where(CollectorProfile.user_id == user.id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise NotFoundError(message="Collector profile not found for this account")

        return CollectorStatsResponse(
            total_lots_collected=profile.total_lots_collected,
            total_weight_kg=float(profile.total_weight_kg),
            trust_score=float(profile.trust_score),
        )

    def _build_response(self, user: User, profile: CollectorProfile) -> CollectorProfileResponse:
        return CollectorProfileResponse(
            id=str(profile.id),
            user_id=str(user.id),
            phone=user.phone,
            full_name=user.full_name,
            collector_type=profile.collector_type,
            preferred_language=user.preferred_language,
            national_id_number=profile.national_id_number,
            national_id_type=profile.national_id_type,
            bank_account_number=profile.bank_account_number,
            ifsc_code=profile.ifsc_code,
            upi_id=profile.upi_id,
            trust_score=float(profile.trust_score),
            total_lots_collected=profile.total_lots_collected,
            total_weight_kg=float(profile.total_weight_kg),
            is_verified=profile.verified_at is not None,
            verified_at=profile.verified_at.isoformat() if profile.verified_at else None,
            created_at=profile.created_at.isoformat() if profile.created_at else "",
        )


collector_service = CollectorService()
