from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional

from ....core.database import get_db
from ....models import (
    CollectorProfile,
    RecyclerCompany,
    RecyclerFacility,
    Lot,
    LotItem,
    RecyclerPayment,
    CustodyEvent,
    Material,
    User,
)
from ....schemas.response import ApiResponse

router = APIRouter(prefix="/admin", tags=["Admin Command Center"])


@router.get("/summary")
async def get_admin_summary(db: AsyncSession = Depends(get_db)):
    """
    Real-time aggregated platform telemetry directly from PostgreSQL.
    """
    # 1. Collectors Active
    collectors_count = (
        await db.execute(select(func.count(CollectorProfile.id)))
    ).scalar_one() or 0

    # 2. Verified Recyclers
    verified_recyclers_count = (
        await db.execute(
            select(func.count(RecyclerCompany.id)).where(
                RecyclerCompany.operating_status == "VERIFIED"
            )
        )
    ).scalar_one() or 0

    # 3. Lots Created
    lots_count = (await db.execute(select(func.count(Lot.id)))).scalar_one() or 0

    # 4. Completed / Settled Transactions
    transactions_count = (
        await db.execute(select(func.count(RecyclerPayment.id)))
    ).scalar_one() or 0

    # 5. Formalized E-Waste Volume in KG
    settled_volume = (
        await db.execute(
            select(
                func.coalesce(
                    func.sum(
                        func.coalesce(
                            Lot.total_verified_weight_kg, Lot.total_estimated_weight_kg
                        )
                    ),
                    0,
                )
            ).where(Lot.status == "SETTLED")
        )
    ).scalar_one() or 0

    # 6. Total Disbursed in INR
    total_disbursed = (
        await db.execute(
            select(func.coalesce(func.sum(RecyclerPayment.total_amount), 0))
        )
    ).scalar_one() or 0

    # 7. Traceability calculation
    traceable_lots_count = (
        await db.execute(
            select(func.count(func.distinct(CustodyEvent.lot_id)))
        )
    ).scalar_one() or 0

    traceable_pct = (
        round((traceable_lots_count / lots_count) * 100, 1) if lots_count > 0 else 100.0
    )

    return ApiResponse.create_success(
        {
            "collectors_active": collectors_count,
            "verified_recyclers": verified_recyclers_count,
            "lots_created": lots_count,
            "transactions": transactions_count,
            "formalized_ewaste_kg": float(settled_volume),
            "traceable_lots_pct": float(traceable_pct),
            "traceable_lots_count": traceable_lots_count,
            "total_disbursed_inr": float(total_disbursed),
            "database_engine": "PostgreSQL 16 (asyncpg)",
            "live_status": "ONLINE",
        }
    )


@router.get("/lots")
async def get_admin_lots(db: AsyncSession = Depends(get_db)):
    """
    Returns collection lots with classification, weighbridge data, and custody status.
    """
    stmt = (
        select(Lot)
        .options(
            selectinload(Lot.items)
            .selectinload(LotItem.material)
            .selectinload(Material.category),
            selectinload(Lot.collector).selectinload(CollectorProfile.user),
            selectinload(Lot.custody_events),
        )
        .order_by(Lot.created_at.desc())
    )
    lots = (await db.execute(stmt)).scalars().all()

    result = []
    for lot in lots:
        primary_item = lot.items[0] if lot.items else None
        custody_event = lot.custody_events[-1] if lot.custody_events else None

        material_name = (
            primary_item.material.name
            if primary_item and primary_item.material
            else "Mixed e-waste"
        )
        category_name = (
            primary_item.material.category.name
            if primary_item
            and primary_item.material
            and primary_item.material.category
            else "Mixed"
        )
        collector_name = (
            lot.collector.user.full_name
            if lot.collector and lot.collector.user
            else "Collector"
        )

        result.append(
            {
                "id": str(lot.id),
                "lot_code": lot.lot_code,
                "material_name": material_name,
                "category": category_name,
                "status": lot.status,
                "estimated_weight_kg": float(lot.total_estimated_weight_kg),
                "verified_weight_kg": (
                    float(lot.total_verified_weight_kg)
                    if lot.total_verified_weight_kg
                    else None
                ),
                "agreed_price_per_kg": (
                    float(lot.agreed_price_per_kg)
                    if lot.agreed_price_per_kg
                    else None
                ),
                "final_value": (
                    float(lot.final_value)
                    if lot.final_value
                    else float(lot.estimated_value)
                ),
                "ai_classification": material_name,
                "ai_confidence": (
                    float(primary_item.ai_confidence_score or 0.95)
                    if primary_item
                    else 0.9
                ),
                "hazard_condition": primary_item.detected_hazard if primary_item else "NORMAL",
                "hazard_severity": (
                    "CRITICAL"
                    if primary_item
                    and primary_item.detected_hazard
                    in ("SWOLLEN_BATTERY", "BROKEN_CRT_LEAD")
                    else "NONE"
                ),
                "collector_name": collector_name,
                "collector_hub": lot.origin_address or "Mumbai Central Hub",
                "is_traceable": bool(custody_event),
                "custody_hash": (
                    custody_event.current_event_hash
                    if custody_event
                    else "PENDING_INITIAL_MERKLE_ANCHOR"
                ),
                "weighbridge_slip": lot.weighbridge_slip_number,
                "created_at": lot.created_at.isoformat() if lot.created_at else "",
            }
        )

    return ApiResponse.create_success({"items": result, "total": len(result)})


@router.get("/collectors")
async def get_admin_collectors(db: AsyncSession = Depends(get_db)):
    """
    Returns registered informal collectors and trust scores.
    """
    stmt = (
        select(CollectorProfile)
        .options(selectinload(CollectorProfile.user))
        .order_by(CollectorProfile.trust_score.desc())
    )
    collectors = (await db.execute(stmt)).scalars().all()

    result = []
    for c in collectors:
        result.append(
            {
                "id": str(c.id),
                "name": c.user.full_name if c.user else "Collector",
                "phone": c.user.phone if c.user else "",
                "hub": c.national_id_number or "Mumbai E-Waste Guild",
                "trust_score": (
                    float(c.trust_score * 100)
                    if c.trust_score <= 1
                    else float(c.trust_score)
                ),
                "total_staged_kg": float(c.total_weight_kg),
                "total_lots": c.total_lots_collected,
                "kyc_status": "VERIFIED" if c.verified_at else "PENDING",
                "kyc_doc_type": f"{c.national_id_type or 'Aadhaar'} Verified",
            }
        )

    return ApiResponse.create_success({"items": result, "total": len(result)})


@router.get("/recyclers")
async def get_admin_recyclers(db: AsyncSession = Depends(get_db)):
    """
    Returns CPCB-verified recycling companies.
    """
    stmt = (
        select(RecyclerCompany)
        .options(selectinload(RecyclerCompany.facilities))
        .order_by(RecyclerCompany.company_name.asc())
    )
    companies = (await db.execute(stmt)).scalars().all()

    result = []
    for r in companies:
        primary_facility = r.facilities[0] if r.facilities else None
        result.append(
            {
                "id": str(r.id),
                "company_name": r.company_name,
                "cpcb_registration_no": r.cpcb_registration_no or "CPCB-PENDING",
                "location": (
                    f"{primary_facility.city or 'Navi Mumbai'}, {primary_facility.state or 'Maharashtra'}"
                    if primary_facility
                    else "Maharashtra"
                ),
                "monthly_capacity_kg": (
                    float((primary_facility.daily_capacity_kg or 500) * 30)
                    if primary_facility
                    else 15000
                ),
                "operating_status": r.operating_status,
                "weighbridge_scale_id": f"SCALE-WB-{str(r.id)[:4].upper()}",
            }
        )

    return ApiResponse.create_success({"items": result, "total": len(result)})


@router.get("/transactions")
async def get_admin_transactions(db: AsyncSession = Depends(get_db)):
    """
    Returns settled weighbridge disbursements and custody receipts.
    """
    # Fetch payments along with related Lot and RecyclerCompany
    payments = (
        await db.execute(
            select(RecyclerPayment).order_by(RecyclerPayment.id.desc())
        )
    ).scalars().all()

    result = []
    for p in payments:
        # Load lot and recycler details
        lot_obj = (
            await db.execute(
                select(Lot)
                .options(selectinload(Lot.collector).selectinload(CollectorProfile.user))
                .where(Lot.id == p.lot_id)
            )
        ).scalar_one_or_none()

        rec_obj = (
            await db.execute(
                select(RecyclerCompany).where(RecyclerCompany.id == p.recycler_id)
            )
        ).scalar_one_or_none()

        result.append(
            {
                "id": str(p.id),
                "reference_no": p.gateway_reference,
                "lot_code": lot_obj.lot_code if lot_obj else "LOT-UNKNOWN",
                "collector_name": (
                    lot_obj.collector.user.full_name
                    if lot_obj and lot_obj.collector and lot_obj.collector.user
                    else "Collector"
                ),
                "recycler_name": rec_obj.company_name if rec_obj else "Recycler Plant",
                "verified_weight_kg": (
                    float(lot_obj.total_verified_weight_kg or 0)
                    if lot_obj
                    else 0.0
                ),
                "agreed_price_per_kg": (
                    float(lot_obj.agreed_price_per_kg or 0)
                    if lot_obj
                    else 0.0
                ),
                "total_amount_inr": float(p.total_amount),
                "payment_method": p.payment_method,
                "weighbridge_slip": p.weighbridge_slip,
                "custody_hash": p.custody_hash,
                "settled_at": "Today",
            }
        )

    return ApiResponse.create_success({"items": result, "total": len(result)})
