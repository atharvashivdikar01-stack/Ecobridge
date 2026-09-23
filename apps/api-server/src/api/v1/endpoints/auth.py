from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.config import settings
from ....core.database import get_db
from ....models.user import User
from ....schemas.response import ApiResponse
from ....schemas.auth import (
    SendOtpRequest,
    SendOtpResponse,
    VerifyOtpRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserSummary,
)
from ....services.otp_service import otp_service
from ....services.auth_service import auth_service
from ...deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/otp/send",
    response_model=ApiResponse[SendOtpResponse],
    status_code=status.HTTP_200_OK,
    summary="Send OTP for Collector Phone Authentication",
    description="Generates a 6-digit One-Time Password for field authentication and zero-barrier login."
)
async def send_otp(request: SendOtpRequest) -> ApiResponse[SendOtpResponse]:
    otp_service.generate_and_send_otp(request.phone)
    return ApiResponse.create_success(
        SendOtpResponse(
            phone=request.phone,
            message="OTP request accepted",
            expires_in_seconds=settings.OTP_EXPIRE_MINUTES * 60,
        )
    )


@router.post(
    "/otp/verify",
    response_model=ApiResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Verify OTP & Login / Auto-Register Collector",
    description="Validates the OTP. Auto-provisions new collector user and profile if not already registered."
)
async def verify_otp(
    request: VerifyOtpRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TokenResponse]:
    token_response = await auth_service.authenticate_collector(
        db=db,
        phone=request.phone,
        otp=request.otp,
        full_name=request.full_name,
        collector_type=request.collector_type or "INDIVIDUAL_PICKER",
        preferred_language=request.preferred_language or "en",
    )
    return ApiResponse.create_success(token_response)


@router.post(
    "/token/refresh",
    response_model=ApiResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Refresh Access Token",
    description="Generates a new access token using a valid refresh token."
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TokenResponse]:
    token_response = await auth_service.refresh_tokens(
        db=db,
        refresh_token=request.refresh_token,
    )
    return ApiResponse.create_success(token_response)


@router.get(
    "/me",
    response_model=ApiResponse[UserSummary],
    status_code=status.HTTP_200_OK,
    summary="Get Current Authenticated User",
    description="Returns the profile summary for the currently authenticated session."
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> ApiResponse[UserSummary]:
    user_summary = UserSummary(
        id=str(current_user.id),
        phone=current_user.phone,
        full_name=current_user.full_name,
        role=current_user.role,
        status=current_user.status,
        preferred_language=current_user.preferred_language,
        avatar_url=current_user.avatar_url,
    )
    return ApiResponse.create_success(user_summary)
