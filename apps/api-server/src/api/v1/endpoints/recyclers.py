from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....models.user import User
from ....schemas.response import ApiResponse
from ....schemas.recycler import (
    RegisterRecyclerRequest,
    UpdateRecyclerCompanyRequest,
    CreateFacilityRequest,
    CreateAuthorizationRequest,
    AuthorizationResponse,
    ConfigureAcceptedMaterialRequest,
    AcceptedMaterialResponse,
    CreateServiceAreaRequest,
    ServiceAreaResponse,
    UpdatePickupAvailabilityRequest,
    PickupAvailabilityResponse,
    VerifyRecyclerRequest,
    VerificationStatusResponse,
    FacilityResponse,
    RecyclerCompanyResponse,
    RecyclerDirectoryListResponse,
)
from ....services.recycler_service import recycler_service
from ...deps import get_current_user, get_current_recycler, get_current_admin

router = APIRouter(prefix="/recyclers", tags=["Verified Recyclers"])


@router.post(
    "/register",
    response_model=ApiResponse[RecyclerCompanyResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register Recycler Company & Primary Facility",
    description="Registers a new certified recycler company with its primary processing facility. Initializes in PENDING_VERIFICATION.",
)
async def register_recycler(
    data: RegisterRecyclerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[RecyclerCompanyResponse]:
    result = await recycler_service.register_recycler(
        db=db,
        user=current_user,
        data=data,
    )
    return ApiResponse.create_success(result)


@router.get(
    "/me",
    response_model=ApiResponse[RecyclerCompanyResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Authenticated Recycler Profile",
    description="Retrieves current recycler's registered company, facilities, authorizations, accepted materials, and service areas.",
)
async def get_my_recycler_profile(
    current_recycler: User = Depends(get_current_recycler),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[RecyclerCompanyResponse]:
    result = await recycler_service.get_recycler_by_user(
        db=db,
        user_id=current_recycler.id,
    )
    return ApiResponse.create_success(result)


@router.put(
    "/me",
    response_model=ApiResponse[RecyclerCompanyResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Recycler Company Profile",
    description="Updates legal company details, contact person, phone, and GST number.",
)
async def update_my_recycler_profile(
    data: UpdateRecyclerCompanyRequest,
    current_recycler: User = Depends(get_current_recycler),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[RecyclerCompanyResponse]:
    result = await recycler_service.update_recycler_company(
        db=db,
        user=current_recycler,
        data=data,
    )
    return ApiResponse.create_success(result)


@router.post(
    "/facilities",
    response_model=ApiResponse[FacilityResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add Processing Facility",
    description="Adds a new processing facility under the authenticated recycler company.",
)
async def add_facility(
    data: CreateFacilityRequest,
    current_recycler: User = Depends(get_current_recycler),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[FacilityResponse]:
    result = await recycler_service.add_facility(
        db=db,
        user=current_recycler,
        data=data,
    )
    return ApiResponse.create_success(result)


@router.post(
    "/facilities/{facility_id}/authorizations",
    response_model=ApiResponse[AuthorizationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add Regulatory Authorization Record",
    description="Attaches a CPCB or SPCB e-waste authorization permit to a facility.",
)
async def add_authorization(
    facility_id: str,
    data: CreateAuthorizationRequest,
    current_recycler: User = Depends(get_current_recycler),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AuthorizationResponse]:
    result = await recycler_service.add_authorization(
        db=db,
        user=current_recycler,
        facility_id=facility_id,
        data=data,
    )
    return ApiResponse.create_success(result)


@router.get(
    "/facilities/{facility_id}/authorizations",
    response_model=ApiResponse[List[AuthorizationResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Facility Authorizations",
    description="Retrieves all regulatory permits for a facility.",
)
async def list_authorizations(
    facility_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[AuthorizationResponse]]:
    result = await recycler_service.list_authorizations(
        db=db,
        facility_id=facility_id,
    )
    return ApiResponse.create_success(result)


@router.post(
    "/{company_id}/verify",
    response_model=ApiResponse[VerificationStatusResponse],
    status_code=status.HTTP_200_OK,
    summary="Admin Recycler Verification Action",
    description="Platform admin action to verify, suspend, or reject a recycler company.",
)
async def verify_recycler(
    company_id: str,
    data: VerifyRecyclerRequest,
    admin_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[VerificationStatusResponse]:
    result = await recycler_service.verify_recycler(
        db=db,
        admin_user=admin_user,
        company_id=company_id,
        data=data,
    )
    return ApiResponse.create_success(result)


@router.post(
    "/facilities/{facility_id}/materials",
    response_model=ApiResponse[AcceptedMaterialResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Configure Accepted Material & Standing Rate",
    description="Configures an accepted e-waste material, standing purchase rate, and minimum weight for a facility.",
)
async def configure_accepted_material(
    facility_id: str,
    data: ConfigureAcceptedMaterialRequest,
    current_recycler: User = Depends(get_current_recycler),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AcceptedMaterialResponse]:
    result = await recycler_service.configure_accepted_material(
        db=db,
        user=current_recycler,
        facility_id=facility_id,
        data=data,
    )
    return ApiResponse.create_success(result)


@router.get(
    "/facilities/{facility_id}/materials",
    response_model=ApiResponse[List[AcceptedMaterialResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Accepted Materials & Rates",
    description="Lists all accepted materials and rates for a facility.",
)
async def list_accepted_materials(
    facility_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[AcceptedMaterialResponse]]:
    result = await recycler_service.list_accepted_materials(
        db=db,
        facility_id=facility_id,
    )
    return ApiResponse.create_success(result)


@router.post(
    "/facilities/{facility_id}/service-areas",
    response_model=ApiResponse[ServiceAreaResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add Service Area Zone",
    description="Configures geographic coverage region, city, pincodes, and radius for a facility.",
)
async def add_service_area(
    facility_id: str,
    data: CreateServiceAreaRequest,
    current_recycler: User = Depends(get_current_recycler),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ServiceAreaResponse]:
    result = await recycler_service.add_service_area(
        db=db,
        user=current_recycler,
        facility_id=facility_id,
        data=data,
    )
    return ApiResponse.create_success(result)


@router.get(
    "/facilities/{facility_id}/service-areas",
    response_model=ApiResponse[List[ServiceAreaResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Service Areas",
    description="Lists all geographic service areas covered by a facility.",
)
async def list_service_areas(
    facility_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[ServiceAreaResponse]]:
    result = await recycler_service.list_service_areas(
        db=db,
        facility_id=facility_id,
    )
    return ApiResponse.create_success(result)


@router.put(
    "/facilities/{facility_id}/pickup",
    response_model=ApiResponse[PickupAvailabilityResponse],
    status_code=status.HTTP_200_OK,
    summary="Configure Pickup Availability",
    description="Configures pickup logistics dispatch flag, minimum weight, maximum distance, and lead times.",
)
async def update_pickup_availability(
    facility_id: str,
    data: UpdatePickupAvailabilityRequest,
    current_recycler: User = Depends(get_current_recycler),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[PickupAvailabilityResponse]:
    result = await recycler_service.update_pickup_availability(
        db=db,
        user=current_recycler,
        facility_id=facility_id,
        data=data,
    )
    return ApiResponse.create_success(result)


@router.get(
    "/directory",
    response_model=ApiResponse[RecyclerDirectoryListResponse],
    status_code=status.HTTP_200_OK,
    summary="Recycler Discovery Directory",
    description="Search directory for collectors and aggregators to discover verified recyclers by accepted material, city, state, or pickup availability.",
)
async def search_directory(
    material_id: Optional[str] = Query(None, description="Filter by accepted material UUID"),
    city: Optional[str] = Query(None, description="Filter by city name"),
    state: Optional[str] = Query(None, description="Filter by state name"),
    postal_code: Optional[str] = Query(None, description="Filter by postal code"),
    pickup_required: Optional[bool] = Query(None, description="Filter for recyclers providing lot pickup logistics"),
    hazardous_required: Optional[bool] = Query(None, description="Filter for facilities certified for hazardous waste"),
    verified_only: bool = Query(True, description="Filter only verified recyclers"),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[RecyclerDirectoryListResponse]:
    result = await recycler_service.search_directory(
        db=db,
        material_id=material_id,
        city=city,
        state=state,
        postal_code=postal_code,
        pickup_required=pickup_required,
        hazardous_required=hazardous_required,
        verified_only=verified_only,
    )
    return ApiResponse.create_success(result)
