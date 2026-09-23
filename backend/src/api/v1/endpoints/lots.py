from typing import Optional
import hashlib
from pathlib import Path

from fastapi import APIRouter, Depends, Header, Request, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....core.config import settings
from ....models.user import User
from ....schemas.response import ApiResponse
from ....schemas.lot import (
    CreateLotRequest,
    CreateLotImageRequest,
    LotResponse,
    LotListResponse,
    LotImageResponse,
    TaxonomyListResponse,
)
from ....services.lot_service import lot_service
from ...deps import get_current_user, get_current_collector

router = APIRouter(prefix="/lots", tags=["Material Lots"])


@router.post(
    "",
    response_model=ApiResponse[LotResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create & Stage E-Waste Material Lot",
    description="Creates a collection batch with line items, material categories, approximate weight, estimated fair value, GPS location, offline timestamps, and photo references. Appends initial cryptographic custody event."
)
async def create_lot(
    lot_data: CreateLotRequest,
    current_collector: User = Depends(get_current_collector),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[LotResponse]:
    lot_response = await lot_service.create_lot(
        db=db,
        collector_user=current_collector,
        data=lot_data,
    )
    return ApiResponse.create_success(lot_response)


@router.get(
    "",
    response_model=ApiResponse[LotListResponse],
    status_code=status.HTTP_200_OK,
    summary="List Collector Lots",
    description="Retrieves paginated material lots created by the authenticated collector with optional status filtering."
)
async def list_lots(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (e.g. COLLECTED, OFFERED, VERIFIED, SETTLED)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_collector: User = Depends(get_current_collector),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[LotListResponse]:
    lots_response = await lot_service.list_collector_lots(
        db=db,
        current_user=current_collector,
        status=status_filter,
        page=page,
        page_size=page_size,
    )
    return ApiResponse.create_success(lots_response)


@router.get(
    "/taxonomy/materials",
    response_model=ApiResponse[TaxonomyListResponse],
    status_code=status.HTTP_200_OK,
    summary="List Material Categories & Benchmark Prices",
    description="Returns active e-waste categories, materials, and price bands for client-side item selection and pricing."
)
async def get_taxonomy(
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TaxonomyListResponse]:
    taxonomy = await lot_service.get_active_taxonomy(db=db)
    return ApiResponse.create_success(taxonomy)


@router.get(
    "/{lot_id}",
    response_model=ApiResponse[LotResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Detailed Lot Information",
    description="Retrieves complete information for a specific lot by its UUID or unique lot code (e.g. EB-202609-XXXX)."
)
async def get_lot(
    lot_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[LotResponse]:
    lot_response = await lot_service.get_lot(
        db=db,
        lot_id_or_code=lot_id,
        current_user=current_user,
    )
    return ApiResponse.create_success(lot_response)


@router.post(
    "/{lot_id}/images",
    response_model=ApiResponse[LotImageResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Attach Photo Reference to Lot",
    description="Attaches an additional photo evidence reference with SHA-256 integrity hash and timestamp."
)
async def attach_image(
    lot_id: str,
    image_data: CreateLotImageRequest,
    current_collector: User = Depends(get_current_collector),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[LotImageResponse]:
    image_response = await lot_service.attach_image(
        db=db,
        lot_id_or_code=lot_id,
        current_user=current_collector,
        image_data=image_data,
    )
    return ApiResponse.create_success(image_response)


@router.post(
    "/{lot_id}/photos",
    response_model=ApiResponse[LotImageResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload lot photo evidence",
)
async def upload_photo(
    lot_id: str,
    request: Request,
    image_sha256: str = Header(..., alias="X-Image-SHA256", min_length=64, max_length=64),
    current_collector: User = Depends(get_current_collector),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[LotImageResponse]:
    """Store an image only after verifying the hash computed by the offline client."""
    content_type = request.headers.get("content-type", "").split(";", 1)[0].lower()
    suffix = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}.get(content_type)
    if suffix is None:
        from ....core.exceptions import ConflictError
        raise ConflictError("Photo must be JPEG, PNG, or WebP")
    body = await request.body()
    if not body or len(body) > settings.MAX_IMAGE_UPLOAD_BYTES:
        from ....core.exceptions import ConflictError
        raise ConflictError("Photo must be between 1 byte and 5 MB")
    actual_hash = hashlib.sha256(body).hexdigest()
    if actual_hash != image_sha256.lower():
        from ....core.exceptions import ConflictError
        raise ConflictError("Photo hash does not match uploaded content")
    media_dir = Path(settings.MEDIA_ROOT) / "lots"
    media_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{actual_hash}{suffix}"
    (media_dir / filename).write_bytes(body)
    image_response = await lot_service.attach_image(
        db=db,
        lot_id_or_code=lot_id,
        current_user=current_collector,
        image_data=CreateLotImageRequest(image_url=f"/media/lots/{filename}", image_hash=actual_hash),
    )
    return ApiResponse.create_success(image_response)
