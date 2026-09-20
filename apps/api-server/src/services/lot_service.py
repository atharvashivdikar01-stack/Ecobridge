import hashlib
import json
import random
import uuid
from decimal import Decimal
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import AppException, NotFoundError, ForbiddenError
from ..models.user import User
from ..models.collector import CollectorProfile
from ..models.taxonomy import WasteCategory, Material, MaterialPriceBand
from ..models.lot import Lot, LotItem, LotImage
from ..models.traceability import CustodyEvent
from ..schemas.lot import (
    CreateLotRequest,
    CreateLotImageRequest,
    LotItemResponse,
    LotImageResponse,
    LotResponse,
    LotListResponse,
    MaterialItemTaxonomy,
    CategoryTaxonomyResponse,
    TaxonomyListResponse,
)


class LotService:
    """Manages e-waste lot creation, line item pricing, photos, and custody logging."""

    async def create_lot(
        self,
        db: AsyncSession,
        collector_user: User,
        data: CreateLotRequest,
    ) -> LotResponse:
        # 1. Fetch Collector Profile
        result = await db.execute(
            select(CollectorProfile).where(CollectorProfile.user_id == collector_user.id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise NotFoundError(message="Collector profile not found for this account")

        # 2. Determine / Generate Lot Code
        if data.lot_code and data.lot_code.strip():
            lot_code = data.lot_code.strip().upper()
        else:
            now_str = datetime.now(timezone.utc).strftime("%Y%m")
            rnd = random.randint(1000, 9999)
            lot_code = f"EB-{now_str}-{rnd}"

        # Check lot code uniqueness
        existing = await db.execute(select(Lot).where(Lot.lot_code == lot_code))
        if existing.scalar_one_or_none():
            lot_code = f"EB-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}"

        # 3. Process Line Items and Calculate Approximate Weight & Fair Value
        total_weight = Decimal("0.000")
        total_value = Decimal("0.00")
        lot_items: List[LotItem] = []

        now_utc = datetime.now(timezone.utc)
        offline_ts = data.offline_created_at or now_utc

        for item_in in data.items:
            try:
                mat_uuid = uuid.UUID(str(item_in.material_id))
            except (ValueError, TypeError):
                raise AppException(
                    code="INVALID_MATERIAL_ID",
                    message=f"Invalid material UUID: {item_in.material_id}",
                    status_code=400,
                )

            # Look up material
            mat_res = await db.execute(select(Material).where(Material.id == mat_uuid))
            material = mat_res.scalar_one_or_none()
            if not material:
                raise NotFoundError(message=f"Material with ID '{item_in.material_id}' not found")

            # Determine Unit Price
            if item_in.unit_price_estimated is not None:
                unit_price = Decimal(str(item_in.unit_price_estimated))
            else:
                # Query active price band benchmark
                pb_res = await db.execute(
                    select(MaterialPriceBand)
                    .where(MaterialPriceBand.material_id == material.id, MaterialPriceBand.is_active == True)
                    .order_by(MaterialPriceBand.effective_from.desc())
                )
                price_band = pb_res.scalars().first()
                unit_price = price_band.benchmark_price_per_unit if price_band else Decimal("150.00")

            weight = Decimal(str(item_in.estimated_weight_kg))
            subtotal = Decimal(str(round(float(weight * unit_price), 2)))

            total_weight += weight
            total_value += subtotal

            lot_item = LotItem(
                material_id=material.id,
                quantity=item_in.quantity,
                unit=item_in.unit,
                estimated_weight_kg=weight,
                unit_price_estimated=unit_price,
                subtotal_estimated=subtotal,
                detected_hazard=item_in.detected_hazard,
                ai_confidence_score=Decimal(str(item_in.ai_confidence_score)) if item_in.ai_confidence_score is not None else None,
                notes=item_in.notes,
            )
            lot_items.append(lot_item)

        # 4. Construct Lot Entity
        lot = Lot(
            lot_code=lot_code,
            collector_id=profile.id,
            status="COLLECTED",
            total_estimated_weight_kg=total_weight,
            estimated_value=total_value,
            currency="INR",
            origin_latitude=Decimal(str(data.origin_latitude)) if data.origin_latitude is not None else None,
            origin_longitude=Decimal(str(data.origin_longitude)) if data.origin_longitude is not None else None,
            origin_address=data.origin_address,
            offline_created_at=offline_ts,
            synced_at=now_utc,
        )
        db.add(lot)
        await db.flush()

        # Attach Items
        for itm in lot_items:
            itm.lot_id = lot.id
            db.add(itm)

        # Attach Images
        if data.images:
            for img_in in data.images:
                img_hash = img_in.image_hash or hashlib.sha256(img_in.image_url.encode("utf-8")).hexdigest()
                lot_image = LotImage(
                    lot_id=lot.id,
                    image_url=img_in.image_url,
                    image_hash=img_hash,
                    latitude=Decimal(str(img_in.latitude)) if img_in.latitude is not None else None,
                    longitude=Decimal(str(img_in.longitude)) if img_in.longitude is not None else None,
                    captured_at=img_in.captured_at or now_utc,
                    is_proof_of_collection=img_in.is_proof_of_collection,
                )
                db.add(lot_image)

        # 5. Log Initial Custody Event (Tamper-evident chain of custody)
        genesis_hash = "0" * 64
        event_payload = {
            "lot_code": lot.lot_code,
            "total_weight_kg": float(total_weight),
            "estimated_value": float(total_value),
            "items_count": len(lot_items),
            "collector_phone": collector_user.phone,
        }
        serialized_payload = json.dumps(event_payload, sort_keys=True)
        hash_preimage = f"{genesis_hash}:{lot.id}:{collector_user.id}:CREATION:{serialized_payload}"
        current_hash = hashlib.sha256(hash_preimage.encode("utf-8")).hexdigest()

        custody_event = CustodyEvent(
            lot_id=lot.id,
            sequence_number=1,
            event_type="CREATION",
            actor_id=collector_user.id,
            actor_role=collector_user.role,
            latitude=lot.origin_latitude,
            longitude=lot.origin_longitude,
            event_timestamp=now_utc,
            event_payload_json=event_payload,
            previous_event_hash=genesis_hash,
            current_event_hash=current_hash,
        )
        db.add(custody_event)

        # 6. Update Collector Aggregates
        profile.total_lots_collected += 1
        profile.total_weight_kg += total_weight

        await db.commit()

        # Reload with selectinload for items and images
        from sqlalchemy.orm import selectinload
        fresh_res = await db.execute(
            select(Lot)
            .where(Lot.id == lot.id)
            .options(
                selectinload(Lot.items).selectinload(LotItem.material).selectinload(Material.category),
                selectinload(Lot.images),
            )
        )
        fresh_lot = fresh_res.scalar_one()
        return self._build_lot_response(fresh_lot, collector_user.full_name)

    async def get_lot(self, db: AsyncSession, lot_id_or_code: str, current_user: User) -> LotResponse:
        """Fetches detailed lot information by UUID or lot code."""
        from sqlalchemy.orm import selectinload
        query = (
            select(Lot)
            .options(
                selectinload(Lot.items).selectinload(LotItem.material).selectinload(Material.category),
                selectinload(Lot.images),
            )
            .where(Lot.lot_code == lot_id_or_code)
        )
        try:
            parsed_uuid = uuid.UUID(str(lot_id_or_code))
            query = (
                select(Lot)
                .options(
                    selectinload(Lot.items).selectinload(LotItem.material).selectinload(Material.category),
                    selectinload(Lot.images),
                )
                .where((Lot.id == parsed_uuid) | (Lot.lot_code == lot_id_or_code))
            )
        except (ValueError, TypeError):
            pass

        result = await db.execute(query)
        lot = result.scalar_one_or_none()
        if not lot:
            raise NotFoundError(message=f"Lot '{lot_id_or_code}' not found")

        # Access check: Collectors can only view their own lots; admins/auditors can view all
        if current_user.role == "COLLECTOR":
            if not current_user.collector_profile or lot.collector_id != current_user.collector_profile.id:
                raise ForbiddenError(message="You do not have permission to view this lot")

        collector_name = current_user.full_name if (current_user.collector_profile and lot.collector_id == current_user.collector_profile.id) else "Verified Collector"
        return self._build_lot_response(lot, collector_name)

    async def list_collector_lots(
        self,
        db: AsyncSession,
        current_user: User,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> LotListResponse:
        """Lists lots belonging to the current collector with pagination."""
        if not current_user.collector_profile:
            return LotListResponse(lots=[], total=0, page=page, page_size=page_size)

        base_filter = [Lot.collector_id == current_user.collector_profile.id]
        if status and status.strip():
            base_filter.append(Lot.status == status.strip().upper())

        # Count total
        count_query = select(func.count()).select_from(Lot).where(*base_filter)
        total = (await db.execute(count_query)).scalar() or 0

        # Query paginated lots with eager loading
        from sqlalchemy.orm import selectinload
        offset = (page - 1) * page_size
        query = (
            select(Lot)
            .where(*base_filter)
            .options(
                selectinload(Lot.items).selectinload(LotItem.material).selectinload(Material.category),
                selectinload(Lot.images),
            )
            .order_by(Lot.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        res = await db.execute(query)
        lots = res.scalars().all()

        lot_responses = [self._build_lot_response(l, current_user.full_name) for l in lots]
        return LotListResponse(lots=lot_responses, total=total, page=page, page_size=page_size)

    async def attach_image(
        self,
        db: AsyncSession,
        lot_id_or_code: str,
        current_user: User,
        image_data: CreateLotImageRequest,
    ) -> LotImageResponse:
        """Attaches a new photo reference to an existing lot."""
        query = select(Lot).where(Lot.lot_code == lot_id_or_code)
        try:
            parsed_uuid = uuid.UUID(str(lot_id_or_code))
            query = select(Lot).where((Lot.id == parsed_uuid) | (Lot.lot_code == lot_id_or_code))
        except (ValueError, TypeError):
            pass

        lot = (await db.execute(query)).scalar_one_or_none()
        if not lot:
            raise NotFoundError(message=f"Lot '{lot_id_or_code}' not found")

        if current_user.role == "COLLECTOR":
            if not current_user.collector_profile or lot.collector_id != current_user.collector_profile.id:
                raise ForbiddenError(message="You do not have permission to modify this lot")

        now_utc = datetime.now(timezone.utc)
        img_hash = image_data.image_hash or hashlib.sha256(image_data.image_url.encode("utf-8")).hexdigest()

        lot_image = LotImage(
            lot_id=lot.id,
            image_url=image_data.image_url,
            image_hash=img_hash,
            latitude=Decimal(str(image_data.latitude)) if image_data.latitude is not None else None,
            longitude=Decimal(str(image_data.longitude)) if image_data.longitude is not None else None,
            captured_at=image_data.captured_at or now_utc,
            is_proof_of_collection=image_data.is_proof_of_collection,
        )
        db.add(lot_image)
        await db.commit()
        await db.refresh(lot_image)

        return LotImageResponse(
            id=str(lot_image.id),
            image_url=lot_image.image_url,
            image_hash=lot_image.image_hash,
            latitude=float(lot_image.latitude) if lot_image.latitude else None,
            longitude=float(lot_image.longitude) if lot_image.longitude else None,
            captured_at=lot_image.captured_at.isoformat(),
            is_proof_of_collection=lot_image.is_proof_of_collection,
        )

    async def get_active_taxonomy(self, db: AsyncSession) -> TaxonomyListResponse:
        """Returns categories and materials with price benchmarks for client staging."""
        res = await db.execute(
            select(WasteCategory).where(WasteCategory.is_active == True).order_by(WasteCategory.name)
        )
        categories = res.scalars().all()

        output_categories: List[CategoryTaxonomyResponse] = []
        for cat in categories:
            materials_out: List[MaterialItemTaxonomy] = []
            for mat in cat.materials:
                if not mat.is_active:
                    continue

                # Benchmark price from active price band
                pb = next((p for p in mat.price_bands if p.is_active), None)
                benchmark = float(pb.benchmark_price_per_unit) if pb else 150.0
                min_p = float(pb.min_price_per_unit) if pb else 100.0
                max_p = float(pb.max_price_per_unit) if pb else 250.0

                materials_out.append(
                    MaterialItemTaxonomy(
                        id=str(mat.id),
                        code=mat.code,
                        name=mat.name,
                        base_unit=mat.base_unit,
                        benchmark_price_per_unit=benchmark,
                        min_price_per_unit=min_p,
                        max_price_per_unit=max_p,
                        default_hazard=cat.default_hazard,
                    )
                )

            output_categories.append(
                CategoryTaxonomyResponse(
                    id=str(cat.id),
                    code=cat.code,
                    name=cat.name,
                    description=cat.description,
                    materials=materials_out,
                )
            )

        return TaxonomyListResponse(categories=output_categories)

    def _build_lot_response(self, lot: Lot, collector_name: str) -> LotResponse:
        items_resp: List[LotItemResponse] = []
        for itm in lot.items:
            mat_name = itm.material.name if itm.material else "Unknown Material"
            mat_code = itm.material.code if itm.material else "UNKNOWN"
            cat_name = itm.material.category.name if (itm.material and itm.material.category) else "General"

            items_resp.append(
                LotItemResponse(
                    id=str(itm.id),
                    material_id=str(itm.material_id),
                    material_name=mat_name,
                    material_code=mat_code,
                    category_name=cat_name,
                    quantity=itm.quantity,
                    unit=itm.unit,
                    estimated_weight_kg=float(itm.estimated_weight_kg),
                    verified_weight_kg=float(itm.verified_weight_kg) if itm.verified_weight_kg else None,
                    unit_price_estimated=float(itm.unit_price_estimated),
                    subtotal_estimated=float(itm.subtotal_estimated),
                    detected_hazard=itm.detected_hazard,
                    ai_confidence_score=float(itm.ai_confidence_score) if itm.ai_confidence_score else None,
                    notes=itm.notes,
                )
            )

        images_resp: List[LotImageResponse] = [
            LotImageResponse(
                id=str(img.id),
                image_url=img.image_url,
                image_hash=img.image_hash,
                latitude=float(img.latitude) if img.latitude else None,
                longitude=float(img.longitude) if img.longitude else None,
                captured_at=img.captured_at.isoformat(),
                is_proof_of_collection=img.is_proof_of_collection,
            )
            for img in lot.images
        ]

        return LotResponse(
            id=str(lot.id),
            lot_code=lot.lot_code,
            collector_id=str(lot.collector_id),
            collector_name=collector_name,
            status=lot.status,
            total_estimated_weight_kg=float(lot.total_estimated_weight_kg),
            total_verified_weight_kg=float(lot.total_verified_weight_kg) if lot.total_verified_weight_kg else None,
            estimated_value=float(lot.estimated_value),
            final_value=float(lot.final_value) if lot.final_value else None,
            currency=lot.currency,
            origin_latitude=float(lot.origin_latitude) if lot.origin_latitude else None,
            origin_longitude=float(lot.origin_longitude) if lot.origin_longitude else None,
            origin_address=lot.origin_address,
            offline_created_at=lot.offline_created_at.isoformat(),
            synced_at=lot.synced_at.isoformat() if lot.synced_at else None,
            created_at=lot.created_at.isoformat(),
            items_count=len(items_resp),
            items=items_resp,
            images=images_resp,
        )


lot_service = LotService()
