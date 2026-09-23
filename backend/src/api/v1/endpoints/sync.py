from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....models import HandoverRecord, Lot, Material, User, WasteCategory
from ....models import RecyclerPayment
from ....schemas.lot import CreateLotRequest
from ....schemas.response import ApiResponse
from ....services.lot_service import lot_service
from ...deps import get_current_collector

router = APIRouter(prefix="/sync", tags=["Offline Sync"])
MOBILE_CATEGORY_CODES = {
    "CRT MONITORS & TVS": "CAT_CRT", "LCD / LED PANELS": "CAT_LCD_LED",
    "PRINTED CIRCUIT BOARDS (PCBS)": "CAT_PCB", "COPPER CABLES & WIRES": "CAT_CABLES",
    "BATTERIES": "CAT_BATTERY", "MOTORS & MAGNET ASSEMBLIES": "CAT_MOTORS",
    "MIXED E-WASTE PLASTICS": "CAT_PLASTICS", "OTHER ELECTRONIC SCRAP": "CAT_OTHER",
}


class Mutation(BaseModel):
    id: str = Field(min_length=1)
    lot_id: str = Field(min_length=1)
    record_type: str = Field(min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: str | None = None


class SyncBatch(BaseModel):
    mutations: list[Mutation] = Field(default_factory=list)
    client_id: str | None = None


class NativeLot(BaseModel):
    uuid: str = Field(min_length=1)
    short_code: str = Field(min_length=1)
    category: str = Field(min_length=1)
    approx_weight_kg: float = Field(gt=0)
    quoted_price: float = Field(ge=0)
    created_at: str | None = None


class NativeSyncBatch(BaseModel):
    collector_uuid: str | None = None
    lots: list[NativeLot] = Field(default_factory=list)


class NativeHandover(BaseModel):
    uuid: str = Field(min_length=1)
    reference_no: str = Field(min_length=1)
    lot_short_code: str = Field(min_length=1)
    recycler_id: str = Field(min_length=1)
    weight: float = Field(gt=0)
    agreed_price: float = Field(ge=0)
    record_hash: str = Field(min_length=64, max_length=64)
    payment_mode: str = Field(min_length=1)
    payment_amount: float = Field(ge=0)
    payment_status: str = Field(min_length=1)
    created_at: datetime


class NativeHandoverBatch(BaseModel):
    handovers: list[NativeHandover] = Field(default_factory=list)


@router.get("/status")
async def collector_sync_status(
    collector: User = Depends(get_current_collector),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict[str, Any]]:
    """Return authoritative server transitions for the device's locally-created records."""
    lots = (await db.execute(select(Lot).where(Lot.collector_id == collector.collector_profile.id))).scalars().all()
    handovers = (await db.execute(select(HandoverRecord).where(HandoverRecord.collector_id == collector.collector_profile.id))).scalars().all()
    payment_by_lot = {
        payment.lot_id: payment
        for payment in (await db.execute(select(RecyclerPayment).where(RecyclerPayment.lot_id.in_([lot.id for lot in lots])))).scalars()
    } if lots else {}
    return ApiResponse.create_success({
        "lots": [{"lot_code": lot.lot_code, "status": lot.status} for lot in lots],
        "handovers": [{
            "reference_no": handover.reference_no,
            "lot_code": next((lot.lot_code for lot in lots if lot.id == handover.lot_id), ""),
            "status": handover.status,
            "payment_status": "PAID" if handover.lot_id in payment_by_lot else handover.payment_status,
            "payment_amount": float(payment_by_lot[handover.lot_id].total_amount) if handover.lot_id in payment_by_lot else None,
        } for handover in handovers],
    })


@router.post("")
async def sync(
    batch: SyncBatch,
    collector: User = Depends(get_current_collector),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for mutation in batch.mutations:
        if mutation.record_type.lower() not in {"lot", "lot creation", "create_lot"}:
            results.append({"id": mutation.id, "status": "REJECTED", "message": "Unsupported mutation type"})
            continue
        existing = (
            await db.execute(
                select(Lot).where(
                    Lot.lot_code == mutation.lot_id,
                    Lot.collector_id == collector.collector_profile.id,
                )
            )
        ).scalar_one_or_none()
        if existing:
            results.append({"id": mutation.id, "lot_id": mutation.lot_id, "status": "SYNCHRONIZED", "duplicate": True})
            continue
        lot_data = CreateLotRequest.model_validate(mutation.payload)
        created = await lot_service.create_lot(db=db, collector_user=collector, data=lot_data)
        results.append({"id": mutation.id, "lot_id": created.id, "lot_code": created.lot_code, "status": "SYNCHRONIZED"})
    return ApiResponse.create_success({
        "synced_count": sum(1 for item in results if item["status"] == "SYNCHRONIZED"),
        "results": results,
        "server_time": datetime.now(timezone.utc).isoformat(),
    })


@router.post("/batch")
async def sync_native_collector_batch(
    batch: NativeSyncBatch,
    collector: User = Depends(get_current_collector),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict[str, Any]]:
    """Compatibility boundary for the native collector app's offline lot queue."""
    synced_lot_ids: list[str] = []
    failed_items: list[str] = []

    for native_lot in batch.lots:
        existing = (
            await db.execute(
                select(Lot).where(
                    Lot.lot_code == native_lot.short_code,
                    Lot.collector_id == collector.collector_profile.id,
                )
            )
        ).scalar_one_or_none()
        if existing:
            synced_lot_ids.append(native_lot.uuid)
            continue

        material = (
            await db.execute(
                select(Material).where(func.lower(Material.name) == native_lot.category.strip().lower())
            )
        ).scalar_one_or_none()
        if not material and native_lot.category.strip().upper() in MOBILE_CATEGORY_CODES:
            material = (await db.execute(
                select(Material).join(Material.category).where(
                    WasteCategory.code == MOBILE_CATEGORY_CODES[native_lot.category.strip().upper()]
                )
            )).scalars().first()
        if not material:
            failed_items.append(native_lot.uuid)
            continue

        try:
            await lot_service.create_lot(
                db=db,
                collector_user=collector,
                data=CreateLotRequest.model_validate({
                    "lot_code": native_lot.short_code,
                    "offline_created_at": native_lot.created_at,
                    "items": [{
                        "material_id": str(material.id),
                        "estimated_weight_kg": native_lot.approx_weight_kg,
                        "unit_price_estimated": native_lot.quoted_price,
                    }],
                }),
            )
            await db.commit()
            synced_lot_ids.append(native_lot.uuid)
        except Exception:
            await db.rollback()
            failed_items.append(native_lot.uuid)

    return ApiResponse.create_success({
        "synced_lot_ids": synced_lot_ids,
        "synced_handover_ids": [],
        "failed_items": failed_items,
    })


@router.post("/handovers")
async def sync_native_handovers(
    batch: NativeHandoverBatch,
    collector: User = Depends(get_current_collector),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict[str, Any]]:
    synced_handover_ids: list[str] = []
    failed_items: list[str] = []
    for handover in batch.handovers:
        existing = (await db.execute(
            select(HandoverRecord).where(HandoverRecord.reference_no == handover.reference_no)
        )).scalar_one_or_none()
        if existing:
            if existing.collector_id == collector.collector_profile.id:
                synced_handover_ids.append(handover.uuid)
            else:
                failed_items.append(handover.uuid)
            continue

        lot = (await db.execute(select(Lot).where(
            Lot.lot_code == handover.lot_short_code,
            Lot.collector_id == collector.collector_profile.id,
        ))).scalar_one_or_none()
        if not lot:
            failed_items.append(handover.uuid)
            continue

        db.add(HandoverRecord(
            lot_id=lot.id,
            collector_id=collector.collector_profile.id,
            reference_no=handover.reference_no,
            requested_recycler_id=handover.recycler_id,
            declared_weight_kg=handover.weight,
            declared_amount=handover.payment_amount,
            payment_mode=handover.payment_mode,
            payment_status="PENDING",
            record_hash=handover.record_hash.lower(),
            collector_created_at=handover.created_at,
        ))
        await db.commit()
        synced_handover_ids.append(handover.uuid)

    return ApiResponse.create_success({
        "synced_lot_ids": [],
        "synced_handover_ids": synced_handover_ids,
        "failed_items": failed_items,
    })
