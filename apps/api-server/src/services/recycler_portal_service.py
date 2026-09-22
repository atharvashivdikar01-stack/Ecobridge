import hashlib
import json
import random
import uuid
from decimal import Decimal
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.exceptions import AppException, ForbiddenError, NotFoundError, ConflictError
from ..core.logging import get_logger
from ..models.user import User
from ..models.recycler import RecyclerCompany
from ..models.lot import Lot, LotItem, LotImage
from ..models.taxonomy import Material, WasteCategory
from ..models.traceability import CustodyEvent
from ..models.pricing import RecyclerOffer
from ..models.transaction import Handover, Transaction
from ..schemas.recycler_portal import (
    AvailableMaterialItem,
    AvailableMaterialsListResponse,
    AcceptOfferRequest,
    ConfirmHandoverRequest,
    RecordPaymentRequest,
    RecyclerTransactionResponse,
    RecyclerLedgerResponse,
    RecyclerDashboardSummary,
)

logger = get_logger("ecobridge.recycler_portal_service")

# Safety guidance lookup for hazardous condition alerts
HAZARD_GUIDANCE = {
    "NORMAL": {
        "severity": "INFO",
        "advisory": "Standard e-waste handling. Check components for dust and wear.",
        "ppe": ["Basic cotton gloves"],
    },
    "SWOLLEN_BATTERY": {
        "severity": "DANGER",
        "advisory": "WARNING: Swollen Li-ion battery pouch detected. Risk of thermal runaway or fire. Do not puncture, crush, or expose to heat.",
        "ppe": ["Fire-retardant gloves", "Face shield", "Non-sparking tongs"],
    },
    "LEAKING_ELECTROLYTE": {
        "severity": "CRITICAL",
        "advisory": "CRITICAL: Chemical leakage detected. Avoid inhalation of fumes and direct skin contact.",
        "ppe": ["Chemical-resistant nitrile gloves", "Respirator mask", "Safety goggles"],
    },
    "BROKEN_CRT_GLASS": {
        "severity": "WARNING",
        "advisory": "Hazardous leaded glass and implosion risk. Vacuum shards; do not sweep dry.",
        "ppe": ["Heavy cut-resistant Kevlar gloves", "Safety goggles", "Steel-toe boots"],
    },
    "BURNT_COMPONENTS": {
        "severity": "WARNING",
        "advisory": "Potential toxic dioxin and heavy metal residue from burnt PCB components.",
        "ppe": ["Nitrile gloves", "N95 particulate respirator"],
    },
}


class RecyclerPortalService:
    """Service handling all recycler portal domain operations: discovery, offer acceptance,
    scale weighbridge verification, handover confirmation, cash/digital payment, and ledger.
    """

    async def get_recycler_company(self, db: AsyncSession, user: User) -> RecyclerCompany:
        """Finds or resolves the recycler company associated with current user."""
        res = await db.execute(select(RecyclerCompany).where(RecyclerCompany.user_id == user.id))
        company = res.scalar_one_or_none()
        if not company:
            # Check if any company exists if user is admin
            if user.role in ("PLATFORM_ADMIN", "RECYCLER_ADMIN"):
                comp_res = await db.execute(select(RecyclerCompany))
                company = comp_res.scalars().first()
        if not company:
            raise NotFoundError("No registered recycler company profile found for this account")
        return company

    async def get_dashboard_summary(self, db: AsyncSession, current_user: User) -> RecyclerDashboardSummary:
        """Calculates dashboard KPI metrics for the authenticated recycler."""
        company = await self.get_recycler_company(db, current_user)
        is_verified = company.operating_status == "VERIFIED"

        # Count available staged lots
        avail_res = await db.execute(
            select(func.count(Lot.id)).where(Lot.status.in_(["COLLECTED", "OFFERED"]))
        )
        avail_count = avail_res.scalar() or 0

        # Count pending offers accepted by this recycler awaiting handover
        pending_handover_res = await db.execute(
            select(func.count(Lot.id)).where(Lot.status == "ACCEPTED")
        )
        pending_handovers = pending_handover_res.scalar() or 0

        # Count completed transactions for this recycler
        tx_count_res = await db.execute(
            select(func.count(Transaction.id)).where(Transaction.recycler_id == company.id)
        )
        completed_tx = tx_count_res.scalar() or 0

        # Aggregate total weight and total payouts
        weight_res = await db.execute(
            select(func.sum(Transaction.verified_weight_kg)).where(Transaction.recycler_id == company.id)
        )
        total_weight = weight_res.scalar() or Decimal("0.000")

        payout_res = await db.execute(
            select(func.sum(Transaction.amount)).where(Transaction.recycler_id == company.id)
        )
        total_payout = payout_res.scalar() or Decimal("0.00")

        return RecyclerDashboardSummary(
            company_name=company.company_name,
            cpcb_registration_no=company.cpcb_registration_no,
            operating_status=company.operating_status,
            is_verified=is_verified,
            available_lots_count=avail_count,
            pending_offers_count=pending_handovers,
            pending_handovers_count=pending_handovers,
            completed_transactions_count=completed_tx,
            total_weight_recycled_kg=float(total_weight),
            total_payouts_inr=float(total_payout),
        )

    async def get_available_materials(
        self,
        db: AsyncSession,
        status_filter: Optional[str] = None,
        material_type: Optional[str] = None,
        hazardous_only: bool = False,
    ) -> AvailableMaterialsListResponse:
        """Lists available collection batches and materials staged by collectors."""
        query = (
            select(Lot)
            .options(
                selectinload(Lot.items).selectinload(LotItem.material).selectinload(Material.category),
                selectinload(Lot.images),
                selectinload(Lot.collector),
            )
            .order_by(Lot.created_at.desc())
        )

        if status_filter and status_filter.strip():
            query = query.where(Lot.status == status_filter.strip().upper())

        res = await db.execute(query)
        lots = res.scalars().all()

        items_out: List[AvailableMaterialItem] = []
        for lot in lots:
            primary_item = lot.items[0] if lot.items else None
            mat_name = primary_item.material.name if (primary_item and primary_item.material) else "Mixed E-Waste"
            mat_code = primary_item.material.code if (primary_item and primary_item.material) else "MIXED"
            mat_id = str(primary_item.material_id) if primary_item else str(uuid.uuid4())
            cat_name = (
                primary_item.material.category.name
                if (primary_item and primary_item.material and primary_item.material.category)
                else "General"
            )

            # AI classification & confidence
            ai_classification = mat_name
            ai_confidence = (
                float(primary_item.ai_confidence_score)
                if (primary_item and primary_item.ai_confidence_score is not None)
                else None
            )

            # Hazard & PPE
            hazard = primary_item.detected_hazard if primary_item else "NORMAL"
            guidance = HAZARD_GUIDANCE.get(hazard, HAZARD_GUIDANCE["NORMAL"])

            if hazardous_only and hazard == "NORMAL":
                continue

            if material_type and material_type.lower() not in mat_name.lower():
                continue

            # Pricing benchmarks
            benchmark = float(primary_item.unit_price_estimated) if primary_item else 150.0
            min_p = round(benchmark * 0.8, 2)
            max_p = round(benchmark * 1.25, 2)

            # Photos
            images = [img.image_url for img in lot.images]
            thumbnail = images[0] if images else None

            # Collector details
            collector_name = "Informal Collector"
            collector_phone = "+91 98XXX XXXXX"
            if lot.collector:
                res_u = await db.execute(select(User).where(User.id == lot.collector.user_id))
                u = res_u.scalar_one_or_none()
                if u:
                    collector_name = u.full_name
                    collector_phone = u.phone

            # Agreed price if already negotiated
            agreed_price = float(primary_item.unit_price_verified) if (primary_item and primary_item.unit_price_verified) else None

            # Final value = verified_weight * agreed_price (or estimated if not yet verified)
            final_val = float(lot.final_value) if lot.final_value is not None else None

            items_out.append(
                AvailableMaterialItem(
                    lot_id=str(lot.id),
                    lot_code=lot.lot_code,
                    collector_id=str(lot.collector_id),
                    collector_name=collector_name,
                    collector_phone=collector_phone,
                    material_id=mat_id,
                    material_code=mat_code,
                    material_name=mat_name,
                    category_name=cat_name,
                    estimated_weight_kg=float(lot.total_estimated_weight_kg),
                    verified_weight_kg=float(lot.total_verified_weight_kg) if lot.total_verified_weight_kg is not None else None,
                    ai_classification=ai_classification,
                    ai_confidence_score=ai_confidence,
                    detected_hazard=hazard,
                    hazard_severity=guidance["severity"],
                    safety_advisory=guidance["advisory"],
                    required_ppe=guidance["ppe"],
                    benchmark_price_per_kg=benchmark,
                    min_price_per_kg=min_p,
                    max_price_per_kg=max_p,
                    agreed_price_per_kg=agreed_price,
                    final_value=final_val,
                    currency=lot.currency,
                    status=lot.status,
                    origin_address=lot.origin_address,
                    latitude=float(lot.origin_latitude) if lot.origin_latitude else None,
                    longitude=float(lot.origin_longitude) if lot.origin_longitude else None,
                    thumbnail_url=thumbnail,
                    images=images,
                    created_at=lot.created_at.isoformat(),
                )
            )

        return AvailableMaterialsListResponse(items=items_out, total=len(items_out))

    async def get_material_detail(self, db: AsyncSession, lot_id: str) -> AvailableMaterialItem:
        """Retrieves detailed information for a single collection batch."""
        res = await db.execute(
            select(Lot)
            .options(
                selectinload(Lot.items).selectinload(LotItem.material).selectinload(Material.category),
                selectinload(Lot.images),
                selectinload(Lot.collector),
            )
            .where((Lot.id == uuid.UUID(lot_id)) if self._is_uuid(lot_id) else (Lot.lot_code == lot_id))
        )
        lot = res.scalar_one_or_none()
        if not lot:
            raise NotFoundError(f"Material collection batch '{lot_id}' not found")

        primary_item = lot.items[0] if lot.items else None
        mat_name = primary_item.material.name if (primary_item and primary_item.material) else "Mixed E-Waste"
        mat_code = primary_item.material.code if (primary_item and primary_item.material) else "MIXED"
        mat_id = str(primary_item.material_id) if primary_item else str(uuid.uuid4())
        cat_name = (
            primary_item.material.category.name
            if (primary_item and primary_item.material and primary_item.material.category)
            else "General"
        )

        ai_classification = mat_name
        ai_confidence = (
            float(primary_item.ai_confidence_score)
            if (primary_item and primary_item.ai_confidence_score is not None)
            else None
        )
        hazard = primary_item.detected_hazard if primary_item else "NORMAL"
        guidance = HAZARD_GUIDANCE.get(hazard, HAZARD_GUIDANCE["NORMAL"])

        benchmark = float(primary_item.unit_price_estimated) if primary_item else 150.0
        min_p = round(benchmark * 0.8, 2)
        max_p = round(benchmark * 1.25, 2)

        images = [img.image_url for img in lot.images]
        thumbnail = images[0] if images else None

        collector_name = "Informal Collector"
        collector_phone = "+91 98XXX XXXXX"
        if lot.collector:
            res_u = await db.execute(select(User).where(User.id == lot.collector.user_id))
            u = res_u.scalar_one_or_none()
            if u:
                collector_name = u.full_name
                collector_phone = u.phone

        agreed_price = float(primary_item.unit_price_verified) if (primary_item and primary_item.unit_price_verified) else None
        final_val = float(lot.final_value) if lot.final_value is not None else None

        return AvailableMaterialItem(
            lot_id=str(lot.id),
            lot_code=lot.lot_code,
            collector_id=str(lot.collector_id),
            collector_name=collector_name,
            collector_phone=collector_phone,
            material_id=mat_id,
            material_code=mat_code,
            material_name=mat_name,
            category_name=cat_name,
            estimated_weight_kg=float(lot.total_estimated_weight_kg),
            verified_weight_kg=float(lot.total_verified_weight_kg) if lot.total_verified_weight_kg is not None else None,
            ai_classification=ai_classification,
            ai_confidence_score=ai_confidence,
            detected_hazard=hazard,
            hazard_severity=guidance["severity"],
            safety_advisory=guidance["advisory"],
            required_ppe=guidance["ppe"],
            benchmark_price_per_kg=benchmark,
            min_price_per_kg=min_p,
            max_price_per_kg=max_p,
            agreed_price_per_kg=agreed_price,
            final_value=final_val,
            currency=lot.currency,
            status=lot.status,
            origin_address=lot.origin_address,
            latitude=float(lot.origin_latitude) if lot.origin_latitude else None,
            longitude=float(lot.origin_longitude) if lot.origin_longitude else None,
            thumbnail_url=thumbnail,
            images=images,
            created_at=lot.created_at.isoformat(),
        )

    async def accept_offer(
        self,
        db: AsyncSession,
        current_user: User,
        lot_id: str,
        data: AcceptOfferRequest,
    ) -> AvailableMaterialItem:
        """Enforces recycler authorization check, validates that AI does not set final price,
        calculates final value = verified_weight * agreed_price, and moves lot to ACCEPTED.
        """
        # 1. Verification Check: Only verified recyclers can accept offers
        company = await self.get_recycler_company(db, current_user)
        if company.operating_status != "VERIFIED":
            raise ForbiddenError(
                message="Only authorized and CPCB-verified recyclers can accept offers or process transactions.",
                details={"operating_status": company.operating_status, "company_name": company.company_name},
            )

        # 2. Fetch Lot
        res = await db.execute(
            select(Lot)
            .options(
                selectinload(Lot.items),
                selectinload(Lot.images),
                selectinload(Lot.custody_events),
            )
            .where((Lot.id == uuid.UUID(lot_id)) if self._is_uuid(lot_id) else (Lot.lot_code == lot_id))
        )
        lot = res.scalar_one_or_none()
        if not lot:
            raise NotFoundError(f"Lot '{lot_id}' not found")

        # 3. Prevent duplicate acceptance
        if lot.status in ("ACCEPTED", "HANDED_OVER", "SETTLED"):
            raise ConflictError(f"Lot '{lot.lot_code}' has already been accepted with status '{lot.status}'")

        # 4. Determine Weight & Calculate Final Value: verified_weight * agreed_price
        agreed_rate = Decimal(str(data.agreed_price_per_kg))
        if data.verified_weight_kg is not None:
            active_weight = Decimal(str(data.verified_weight_kg))
            lot.total_verified_weight_kg = active_weight
        elif lot.total_verified_weight_kg is not None:
            active_weight = lot.total_verified_weight_kg
        else:
            active_weight = lot.total_estimated_weight_kg

        final_transaction_value = Decimal(str(round(float(active_weight * agreed_rate), 2)))
        lot.final_value = final_transaction_value
        lot.status = "ACCEPTED"
        lot.designated_facility_id = company.facilities[0].id if company.facilities else None

        # Update primary line item
        if lot.items:
            primary = lot.items[0]
            primary.unit_price_verified = agreed_rate
            primary.subtotal_final = final_transaction_value
            if data.verified_weight_kg:
                primary.verified_weight_kg = Decimal(str(data.verified_weight_kg))

        # 5. Create RecyclerOffer record
        now_utc = datetime.now(timezone.utc)
        offer = RecyclerOffer(
            lot_id=lot.id,
            recycler_id=company.id,
            recycler_name=company.company_name,
            offered_price_per_unit=agreed_rate,
            offered_total_price=final_transaction_value,
            pickup_cost_deduction=Decimal("0.00"),
            net_collector_earning=final_transaction_value,
            currency="INR",
            status="ACCEPTED",
            expires_at=now_utc,
        )
        db.add(offer)

        # 6. Append SHA-256 Custody Event (Deterministic Traceability)
        prev_hash = lot.custody_events[-1].current_event_hash if lot.custody_events else "0" * 64
        seq = len(lot.custody_events) + 1
        event_payload = {
            "event": "OFFER_ACCEPTED",
            "lot_code": lot.lot_code,
            "recycler_id": str(company.id),
            "recycler_name": company.company_name,
            "agreed_price_per_kg": float(agreed_rate),
            "active_weight_kg": float(active_weight),
            "final_value": float(final_transaction_value),
        }
        serialized = json.dumps(event_payload, sort_keys=True)
        hash_input = f"{prev_hash}:{lot.id}:{current_user.id}:OFFER_ACCEPTED:{serialized}"
        cur_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

        custody_event = CustodyEvent(
            lot_id=lot.id,
            sequence_number=seq,
            event_type="OFFER_ACCEPTED",
            actor_id=current_user.id,
            actor_role=current_user.role,
            event_timestamp=now_utc,
            event_payload_json=event_payload,
            previous_event_hash=prev_hash,
            current_event_hash=cur_hash,
        )
        db.add(custody_event)
        await db.commit()

        logger.info(
            f"Offer accepted for lot {lot.lot_code} by {company.company_name}. "
            f"Agreed rate: ₹{agreed_rate}/kg, Final Value: ₹{final_transaction_value}"
        )
        return await self.get_material_detail(db, str(lot.id))

    async def confirm_handover(
        self,
        db: AsyncSession,
        current_user: User,
        lot_id: str,
        data: ConfirmHandoverRequest,
    ) -> AvailableMaterialItem:
        """Confirms physical handover at certified recycling facility with scale weighbridge
        slip reconciliation and appends cryptographic custody event.
        """
        company = await self.get_recycler_company(db, current_user)
        if company.operating_status != "VERIFIED":
            raise ForbiddenError("Only authorized and CPCB-verified recyclers can confirm handovers")

        res = await db.execute(
            select(Lot)
            .options(
                selectinload(Lot.items),
                selectinload(Lot.custody_events),
                selectinload(Lot.collector),
            )
            .where((Lot.id == uuid.UUID(lot_id)) if self._is_uuid(lot_id) else (Lot.lot_code == lot_id))
        )
        lot = res.scalar_one_or_none()
        if not lot:
            raise NotFoundError(f"Lot '{lot_id}' not found")

        # Net scale verified weight
        net_scale_weight = Decimal(str(data.verified_weight_kg))
        lot.total_verified_weight_kg = net_scale_weight

        # Re-evaluate final value: verified weight x agreed price
        agreed_rate = (
            lot.items[0].unit_price_verified
            if (lot.items and lot.items[0].unit_price_verified)
            else (lot.items[0].unit_price_estimated if lot.items else Decimal("150.00"))
        )
        final_val = Decimal(str(round(float(net_scale_weight * agreed_rate), 2)))
        lot.final_value = final_val
        lot.status = "HANDED_OVER"

        if lot.items:
            lot.items[0].verified_weight_kg = net_scale_weight
            lot.items[0].subtotal_final = final_val

        now_utc = datetime.now(timezone.utc)
        manifest_payload = f"{lot.lot_code}:{data.weighbridge_slip_number}:{net_scale_weight}:{now_utc.isoformat()}"
        signed_manifest_hash = hashlib.sha256(manifest_payload.encode("utf-8")).hexdigest()

        # Create Handover Record
        facility_id = uuid.UUID(data.facility_id) if (data.facility_id and self._is_uuid(data.facility_id)) else (
            company.facilities[0].id if company.facilities else None
        )
        handover = Handover(
            lot_id=lot.id,
            facility_id=facility_id,
            recycler_id=company.id,
            collector_id=lot.collector_id,
            handover_type="COLLECTOR_TO_FACILITY",
            weighbridge_slip_number=data.weighbridge_slip_number,
            weighbridge_gross_kg=Decimal(str(data.weighbridge_gross_kg)) if data.weighbridge_gross_kg else None,
            weighbridge_tare_kg=Decimal(str(data.weighbridge_tare_kg)) if data.weighbridge_tare_kg else None,
            weighbridge_net_kg=net_scale_weight,
            scale_calibration_id=data.scale_calibration_id,
            signed_manifest_hash=signed_manifest_hash,
            status="COMPLETED",
            handed_over_at=now_utc,
        )
        db.add(handover)

        # Append Custody Event
        prev_hash = lot.custody_events[-1].current_event_hash if lot.custody_events else "0" * 64
        seq = len(lot.custody_events) + 1
        event_payload = {
            "event": "HANDOVER_CONFIRMED",
            "lot_code": lot.lot_code,
            "weighbridge_slip": data.weighbridge_slip_number,
            "verified_scale_weight_kg": float(net_scale_weight),
            "final_value": float(final_val),
            "manifest_hash": signed_manifest_hash,
        }
        serialized = json.dumps(event_payload, sort_keys=True)
        hash_input = f"{prev_hash}:{lot.id}:{current_user.id}:HANDOVER_CONFIRMED:{serialized}"
        cur_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

        custody_event = CustodyEvent(
            lot_id=lot.id,
            sequence_number=seq,
            event_type="HANDOVER_CONFIRMED",
            actor_id=current_user.id,
            actor_role=current_user.role,
            event_timestamp=now_utc,
            event_payload_json=event_payload,
            previous_event_hash=prev_hash,
            current_event_hash=cur_hash,
            digital_signature=signed_manifest_hash,
        )
        db.add(custody_event)
        await db.commit()

        logger.info(
            f"Handover confirmed for lot {lot.lot_code}. Slip: {data.weighbridge_slip_number}, "
            f"Verified Weight: {net_scale_weight} kg, Value: ₹{final_val}"
        )
        return await self.get_material_detail(db, str(lot.id))

    async def record_payment(
        self,
        db: AsyncSession,
        current_user: User,
        lot_id: str,
        data: RecordPaymentRequest,
    ) -> RecyclerTransactionResponse:
        """Records payment settlement (Cash by default or Optional Digital UPI/IMPS)
        and adds transaction to immutable ledger.
        """
        company = await self.get_recycler_company(db, current_user)
        if company.operating_status != "VERIFIED":
            raise ForbiddenError("Only authorized and CPCB-verified recyclers can record payments")

        res = await db.execute(
            select(Lot)
            .options(
                selectinload(Lot.items).selectinload(LotItem.material),
                selectinload(Lot.custody_events),
                selectinload(Lot.collector),
            )
            .where((Lot.id == uuid.UUID(lot_id)) if self._is_uuid(lot_id) else (Lot.lot_code == lot_id))
        )
        lot = res.scalar_one_or_none()
        if not lot:
            raise NotFoundError(f"Lot '{lot_id}' not found")

        # Check existing transaction
        existing_tx_res = await db.execute(select(Transaction).where(Transaction.lot_id == lot.id))
        if existing_tx_res.scalar_one_or_none():
            raise ConflictError(f"Transaction has already been recorded and settled for lot '{lot.lot_code}'")

        primary_item = lot.items[0] if lot.items else None
        mat_name = primary_item.material.name if (primary_item and primary_item.material) else "Mixed E-Waste"
        verified_weight = lot.total_verified_weight_kg or lot.total_estimated_weight_kg
        agreed_rate = (
            primary_item.unit_price_verified
            if (primary_item and primary_item.unit_price_verified)
            else (primary_item.unit_price_estimated if primary_item else Decimal("150.00"))
        )

        amount_paid = Decimal(str(data.amount))
        payment_method = data.payment_method.upper()

        now_utc = datetime.now(timezone.utc)
        ref_prefix = "EB-CASH" if payment_method == "CASH" else "EB-DIGITAL"
        reference_number = f"{ref_prefix}-{now_utc.strftime('%Y%m%d')}-{random.randint(10000, 99999)}"
        gateway_ref = data.gateway_reference or f"RECEIPT-{random.randint(100000, 999999)}"

        transaction = Transaction(
            reference_number=reference_number,
            transaction_type="COLLECTOR_PAYOUT",
            lot_id=lot.id,
            recycler_id=company.id,
            collector_id=lot.collector_id,
            material_name=mat_name,
            verified_weight_kg=verified_weight,
            agreed_price_per_kg=agreed_rate,
            amount=amount_paid,
            currency="INR",
            payment_method=payment_method,
            payment_status="PAID",
            gateway_reference=gateway_ref,
            status="SETTLED",
            notes=data.notes,
            settled_at=now_utc,
        )
        db.add(transaction)

        # Update lot status to SETTLED
        lot.status = "SETTLED"
        lot.final_value = amount_paid

        # Append Custody Event
        prev_hash = lot.custody_events[-1].current_event_hash if lot.custody_events else "0" * 64
        seq = len(lot.custody_events) + 1
        event_payload = {
            "event": "PAYMENT_SETTLED",
            "reference_number": reference_number,
            "payment_method": payment_method,
            "amount_inr": float(amount_paid),
            "gateway_reference": gateway_ref,
            "collector_id": str(lot.collector_id),
        }
        serialized = json.dumps(event_payload, sort_keys=True)
        hash_input = f"{prev_hash}:{lot.id}:{current_user.id}:PAYMENT_SETTLED:{serialized}"
        cur_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

        custody_event = CustodyEvent(
            lot_id=lot.id,
            sequence_number=seq,
            event_type="PAYMENT_DISBURSED",
            actor_id=current_user.id,
            actor_role=current_user.role,
            event_timestamp=now_utc,
            event_payload_json=event_payload,
            previous_event_hash=prev_hash,
            current_event_hash=cur_hash,
        )
        db.add(custody_event)
        await db.commit()

        # Collector details for response
        collector_name = "Informal Collector"
        collector_phone = "+91 98XXX XXXXX"
        if lot.collector:
            res_u = await db.execute(select(User).where(User.id == lot.collector.user_id))
            u = res_u.scalar_one_or_none()
            if u:
                collector_name = u.full_name
                collector_phone = u.phone

        # Handover slip
        ho_res = await db.execute(select(Handover).where(Handover.lot_id == lot.id))
        ho = ho_res.scalar_one_or_none()
        slip = ho.weighbridge_slip_number if ho else None
        handed_at = ho.handed_over_at.isoformat() if ho else None

        return RecyclerTransactionResponse(
            transaction_id=str(transaction.id),
            reference_number=transaction.reference_number,
            lot_id=str(lot.id),
            lot_code=lot.lot_code,
            collector_id=str(lot.collector_id),
            collector_name=collector_name,
            collector_phone=collector_phone,
            material_name=mat_name,
            verified_weight_kg=float(verified_weight),
            agreed_price_per_kg=float(agreed_rate),
            total_amount=float(amount_paid),
            currency="INR",
            payment_method=payment_method,
            payment_status="PAID",
            gateway_reference=gateway_ref,
            weighbridge_slip=slip,
            custody_hash=cur_hash,
            handed_over_at=handed_at,
            settled_at=now_utc.isoformat(),
            created_at=transaction.created_at.isoformat(),
        )

    async def get_recycler_ledger(
        self,
        db: AsyncSession,
        current_user: User,
    ) -> RecyclerLedgerResponse:
        """Retrieves all transactions and accounting ledger entries for this recycler."""
        company = await self.get_recycler_company(db, current_user)

        res = await db.execute(
            select(Transaction)
            .options(
                selectinload(Transaction.lot).selectinload(Lot.collector),
            )
            .where(Transaction.recycler_id == company.id)
            .order_by(Transaction.created_at.desc())
        )
        transactions = res.scalars().all()

        tx_list: List[RecyclerTransactionResponse] = []
        total_volume = Decimal("0.000")
        total_payout = Decimal("0.00")

        for tx in transactions:
            total_volume += tx.verified_weight_kg
            total_payout += tx.amount

            collector_name = "Collector"
            collector_phone = ""
            if tx.lot and tx.lot.collector:
                res_u = await db.execute(select(User).where(User.id == tx.lot.collector.user_id))
                u = res_u.scalar_one_or_none()
                if u:
                    collector_name = u.full_name
                    collector_phone = u.phone

            # Query custody hash for this lot
            ch_res = await db.execute(
                select(CustodyEvent)
                .where(CustodyEvent.lot_id == tx.lot_id)
                .order_by(CustodyEvent.sequence_number.desc())
            )
            last_event = ch_res.scalars().first()
            custody_hash = last_event.current_event_hash if last_event else None

            # Handover slip
            ho_res = await db.execute(select(Handover).where(Handover.lot_id == tx.lot_id))
            ho = ho_res.scalar_one_or_none()
            slip = ho.weighbridge_slip_number if ho else None
            handed_at = ho.handed_over_at.isoformat() if ho else None

            tx_list.append(
                RecyclerTransactionResponse(
                    transaction_id=str(tx.id),
                    reference_number=tx.reference_number,
                    lot_id=str(tx.lot_id),
                    lot_code=tx.lot.lot_code if tx.lot else "LOT-UNKNOWN",
                    collector_id=str(tx.collector_id),
                    collector_name=collector_name,
                    collector_phone=collector_phone,
                    material_name=tx.material_name,
                    verified_weight_kg=float(tx.verified_weight_kg),
                    agreed_price_per_kg=float(tx.agreed_price_per_kg),
                    total_amount=float(tx.amount),
                    currency=tx.currency,
                    payment_method=tx.payment_method,
                    payment_status=tx.payment_status,
                    gateway_reference=tx.gateway_reference,
                    weighbridge_slip=slip,
                    custody_hash=custody_hash,
                    handed_over_at=handed_at,
                    settled_at=tx.settled_at.isoformat() if tx.settled_at else None,
                    created_at=tx.created_at.isoformat(),
                )
            )

        return RecyclerLedgerResponse(
            transactions=tx_list,
            total_volume_kg=float(total_volume),
            total_disbursed_inr=float(total_payout),
            total_transactions=len(tx_list),
        )

    def _is_uuid(self, val: str) -> bool:
        try:
            uuid.UUID(str(val))
            return True
        except (ValueError, TypeError):
            return False


recycler_portal_service = RecyclerPortalService()
