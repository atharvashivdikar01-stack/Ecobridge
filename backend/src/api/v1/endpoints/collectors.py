from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....models.user import User
from ....schemas.response import ApiResponse
from ....schemas.collector import (
    CollectorProfileResponse,
    CollectorProfileUpdate,
    CollectorKycSubmission,
    CollectorStatsResponse,
)
from ....services.collector_service import collector_service
from ...deps import get_current_collector

router = APIRouter(prefix="/collectors", tags=["Collector Profiles"])


@router.get(
    "/profile",
    response_model=ApiResponse[CollectorProfileResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Collector Profile",
    description="Retrieves the full profile, collection metrics, trust score, and payment coordinates for the authenticated collector."
)
async def get_profile(
    current_collector: User = Depends(get_current_collector),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CollectorProfileResponse]:
    profile = await collector_service.get_profile(db=db, user=current_collector)
    return ApiResponse.create_success(profile)


@router.patch(
    "/profile",
    response_model=ApiResponse[CollectorProfileResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Collector Profile",
    description="Updates collector display name, vernacular language preference, UPI ID, or bank account details."
)
async def update_profile(
    update_data: CollectorProfileUpdate,
    current_collector: User = Depends(get_current_collector),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CollectorProfileResponse]:
    updated = await collector_service.update_profile(
        db=db,
        user=current_collector,
        update_data=update_data,
    )
    return ApiResponse.create_success(updated)


@router.post(
    "/profile/kyc",
    response_model=ApiResponse[CollectorProfileResponse],
    status_code=status.HTTP_200_OK,
    summary="Submit Collector KYC Document",
    description="Submits Aadhaar, Voter ID, or PAN details for informal collector verification."
)
async def submit_kyc(
    kyc_data: CollectorKycSubmission,
    current_collector: User = Depends(get_current_collector),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CollectorProfileResponse]:
    updated = await collector_service.submit_kyc(
        db=db,
        user=current_collector,
        kyc_data=kyc_data,
    )
    return ApiResponse.create_success(updated)


@router.get(
    "/profile/stats",
    response_model=ApiResponse[CollectorStatsResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Collector Performance Stats",
    description="Returns aggregate performance metrics: total lots collected, total weight in kg, and current trust score."
)
async def get_stats(
    current_collector: User = Depends(get_current_collector),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CollectorStatsResponse]:
    stats = await collector_service.get_stats(db=db, user=current_collector)
    return ApiResponse.create_success(stats)
