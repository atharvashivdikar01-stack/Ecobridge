import math
import uuid
from decimal import Decimal
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import AppException, NotFoundError, ValidationError, ForbiddenError
from ..models.taxonomy import Material
from ..models.lot import Lot, LotItem
from ..models.recycler import (
    RecyclerCompany,
    RecyclerFacility,
    AuthorizationRecord,
    RecyclerAcceptedMaterial,
    RecyclerServiceArea,
)
from ..models.pricing import RecyclerOffer
from ..schemas.matching import (
    MatchingItemInput,
    EvaluateManifestRequest,
    MaterialCompatibilityItem,
    MatchingFinancialBreakdown,
    MatchingLogisticsBreakdown,
    MatchingComplianceBreakdown,
    RecyclerMatchCandidate,
    LotMatchingResponse,
)


class MatchingService:
    """Intelligent, explainable recycler matching engine.
    
    Invariants:
    - Grounded in deterministic facts: authorization, compatibility, distance, transport cost, and net earnings.
    - Safety first: disqualifies facilities lacking hazardous authorization when hazardous scrap is present.
    - Zero opaque scores: returns explainable financial and logistics breakdowns with clear pros and cons.
    """

    @staticmethod
    def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great-circle distance between two GPS coordinates in kilometers."""
        earth_radius_km = 6371.0
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = (
            math.sin(d_lat / 2.0) ** 2
            + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return round(earth_radius_km * c, 2)

    async def match_lot(
        self,
        db: AsyncSession,
        lot_id: str,
        require_pickup: bool = False,
        max_distance_km: Optional[float] = None,
        current_user=None,
    ) -> LotMatchingResponse:
        """Match an existing collection lot against certified recyclers."""
        try:
            lot_uuid = uuid.UUID(str(lot_id))
        except ValueError:
            raise ValidationError(message="Invalid lot ID format")

        lot_res = await db.execute(
            select(Lot)
            .where(Lot.id == lot_uuid)
            .options(
                selectinload(Lot.items).selectinload(LotItem.material),
            )
        )
        lot = lot_res.scalar_one_or_none()
        if not lot:
            raise NotFoundError(message=f"Lot with ID '{lot_id}' not found")
        if current_user is not None and current_user.role == "COLLECTOR":
            if not current_user.collector_profile or lot.collector_id != current_user.collector_profile.id:
                raise ForbiddenError(message="You do not have permission to match this lot")

        items_input: List[MatchingItemInput] = []
        for item in lot.items:
            items_input.append(
                MatchingItemInput(
                    material_id=str(item.material_id),
                    weight_kg=float(item.estimated_weight_kg),
                    detected_hazard=item.detected_hazard or "NORMAL",
                )
            )

        origin_lat = float(lot.origin_latitude) if lot.origin_latitude is not None else None
        origin_lon = float(lot.origin_longitude) if lot.origin_longitude is not None else None

        return await self._evaluate_candidates(
            db=db,
            items=items_input,
            origin_lat=origin_lat,
            origin_lon=origin_lon,
            require_pickup=require_pickup,
            max_distance_km=max_distance_km,
            lot_id=str(lot.id),
        )

    async def evaluate_manifest(
        self,
        db: AsyncSession,
        request: EvaluateManifestRequest,
    ) -> LotMatchingResponse:
        """Evaluate an ad-hoc manifest/items list before lot staging."""
        return await self._evaluate_candidates(
            db=db,
            items=request.items,
            origin_lat=request.origin_latitude,
            origin_lon=request.origin_longitude,
            require_pickup=request.require_pickup,
            max_distance_km=request.max_distance_km,
            lot_id=None,
        )

    async def _evaluate_candidates(
        self,
        db: AsyncSession,
        items: List[MatchingItemInput],
        origin_lat: Optional[float],
        origin_lon: Optional[float],
        require_pickup: bool,
        max_distance_km: Optional[float],
        lot_id: Optional[str],
    ) -> LotMatchingResponse:
        """Core evaluation engine matching items against active verified recyclers."""
        total_weight_kg = sum(item.weight_kg for item in items)
        has_hazardous_items = any(item.detected_hazard != "NORMAL" for item in items)

        # 1. Fetch material metadata
        mat_ids = [uuid.UUID(item.material_id) for item in items]
        mat_res = await db.execute(select(Material).where(Material.id.in_(mat_ids)))
        materials_by_id = {str(m.id): m for m in mat_res.scalars().all()}

        # 2. Fetch all verified recyclers and active facilities
        fac_res = await db.execute(
            select(RecyclerFacility)
            .join(RecyclerCompany, RecyclerFacility.recycler_id == RecyclerCompany.id)
            .where(
                RecyclerFacility.is_active == True,
                RecyclerCompany.operating_status == "VERIFIED",
            )
            .options(
                selectinload(RecyclerFacility.company),
                selectinload(RecyclerFacility.authorizations),
                selectinload(RecyclerFacility.accepted_materials).selectinload(RecyclerAcceptedMaterial.material),
                selectinload(RecyclerFacility.service_areas),
            )
        )
        facilities = fac_res.scalars().all()

        # Check existing lot-specific offers if lot_id given
        offers_by_facility: Dict[str, RecyclerOffer] = {}
        if lot_id:
            off_res = await db.execute(
                select(RecyclerOffer).where(
                    RecyclerOffer.lot_id == uuid.UUID(lot_id),
                    RecyclerOffer.status == "OFFERED",
                    RecyclerOffer.expires_at > datetime.now(timezone.utc),
                )
            )
            for offer in off_res.scalars().all():
                offers_by_facility[str(offer.recycler_id)] = offer

        candidates: List[RecyclerMatchCandidate] = []

        for fac in facilities:
            comp = fac.company
            fac_lat = float(fac.latitude)
            fac_lon = float(fac.longitude)

            # 3. Distance calculation
            if origin_lat is not None and origin_lon is not None:
                distance_km = self.haversine_distance_km(origin_lat, origin_lon, fac_lat, fac_lon)
            else:
                distance_km = 15.0  # Default local distance estimate when coordinates missing

            # 4. Compliance & Hazard Check
            active_permits = [
                a for a in (fac.authorizations or [])
                if a.status == "ACTIVE" and a.expiry_date >= datetime.now(timezone.utc).date()
            ]
            has_hazardous_permit = any(
                p.permit_type in ("HAZARDOUS_WASTE_AUTHORIZATION", "E_WASTE_RECYCLER")
                for p in active_permits
            )
            hazard_cleared = True
            is_disqualified_hazard = False

            if has_hazardous_items:
                if not fac.accepts_hazardous or not has_hazardous_permit:
                    hazard_cleared = False
                    is_disqualified_hazard = True

            compliance = MatchingComplianceBreakdown(
                is_verified_recycler=True,
                cpcb_authorized=len(active_permits) > 0,
                accepts_hazardous=fac.accepts_hazardous,
                active_permits_count=len(active_permits),
                hazard_compatibility_cleared=hazard_cleared,
            )

            # 5. Material Compatibility & Rate Calculation
            accepted_map = {
                str(am.material_id): float(am.standard_rate_per_unit)
                for am in (fac.accepted_materials or [])
                if am.is_active
            }

            mat_items: List[MaterialCompatibilityItem] = []
            gross_payout = 0.0
            accepted_count = 0

            for item in items:
                mat = materials_by_id.get(item.material_id)
                mat_name = mat.name if mat else "Unknown Material"
                mat_code = mat.code if mat else "UNKNOWN"

                rate = accepted_map.get(item.material_id)
                if rate is not None:
                    is_acc = True
                    accepted_count += 1
                    sub = round(item.weight_kg * rate, 2)
                    gross_payout += sub
                else:
                    is_acc = False
                    rate = None
                    sub = 0.0

                mat_items.append(
                    MaterialCompatibilityItem(
                        material_id=item.material_id,
                        material_code=mat_code,
                        material_name=mat_name,
                        weight_kg=item.weight_kg,
                        is_accepted=is_acc,
                        offered_rate_per_unit=rate,
                        subtotal=sub,
                        detected_hazard=item.detected_hazard,
                    )
                )

            # If existing direct offer exists, honor offer total price
            existing_offer = offers_by_facility.get(str(comp.id)) or offers_by_facility.get(str(fac.id))
            if existing_offer:
                gross_payout = float(existing_offer.offered_total_price)

            # 6. Logistics & Transport Cost
            pickup_eligible = False
            pickup_mode = "COLLECTOR_SELF_TRANSPORT"
            pickup_subsidy = 0.0
            transport_cost = 0.0

            if fac.pickup_available:
                min_w = float(fac.min_pickup_weight_kg)
                max_d = float(fac.max_pickup_distance_km)
                if total_weight_kg >= min_w and distance_km <= max_d:
                    pickup_eligible = True
                    if distance_km <= 25.0:
                        pickup_mode = "FREE_RECYCLER_PICKUP"
                        transport_cost = 0.0
                        pickup_subsidy = 250.0
                    else:
                        pickup_mode = "SUBSIDIZED_RECYCLER_PICKUP"
                        transport_cost = round((distance_km - 25.0) * 8.0, 2)
                        pickup_subsidy = 200.0

            if not pickup_eligible:
                pickup_mode = "COLLECTOR_SELF_TRANSPORT"
                # Third-party transporter logistics formula: base fare 150 + ₹12/km + ₹1.2/kg
                transport_cost = round(150.0 + (distance_km * 12.0) + (total_weight_kg * 1.2), 2)
                pickup_subsidy = 0.0

            logistics = MatchingLogisticsBreakdown(
                distance_km=distance_km,
                pickup_available=fac.pickup_available,
                pickup_mode=pickup_mode,
                min_pickup_weight_kg=float(fac.min_pickup_weight_kg),
                lead_time_hours=fac.lead_time_hours,
                pickup_operating_days=fac.pickup_operating_days,
            )

            # 7. Net Collector Earnings
            net_earnings = max(0.0, round(gross_payout - transport_cost, 2))

            financial = MatchingFinancialBreakdown(
                gross_payout=round(gross_payout, 2),
                transport_cost=round(transport_cost, 2),
                pickup_subsidy=round(pickup_subsidy, 2),
                net_collector_earnings=round(net_earnings, 2),
                currency="INR",
            )

            # 8. Determine Compatibility Status
            if is_disqualified_hazard:
                status = "DISQUALIFIED_HAZARD"
            elif max_distance_km and distance_km > max_distance_km:
                status = "OUT_OF_RANGE"
            elif accepted_count == len(items):
                status = "FULLY_COMPATIBLE"
            elif accepted_count > 0:
                status = "PARTIALLY_COMPATIBLE"
            else:
                status = "INCOMPATIBLE_MATERIALS"

            # 9. Formulate Transparent Narrative & Pros/Cons
            pros: List[str] = []
            cons: List[str] = []

            if is_disqualified_hazard:
                explanation = (
                    f"Disqualified: This lot contains hazardous e-waste ({[i.detected_hazard for i in items if i.detected_hazard != 'NORMAL']}), "
                    f"but {fac.facility_name} lacks authorized hazardous handling consent from CPCB/SPCB."
                )
                cons.append("Cannot handle hazardous materials in this lot")
            else:
                explanation = (
                    f"{comp.company_name} ({fac.facility_name}) offers estimated net earnings of ₹{net_earnings:,.2f} "
                    f"({round((net_earnings / gross_payout * 100) if gross_payout > 0 else 0)}% of gross value). "
                )
                if pickup_mode == "FREE_RECYCLER_PICKUP":
                    explanation += f"Includes 100% free doorstep pickup ({distance_km} km away). "
                    pros.append(f"Free facility pickup ({distance_km} km)")
                elif pickup_mode == "SUBSIDIZED_RECYCLER_PICKUP":
                    explanation += f"Includes subsidized facility pickup with only ₹{transport_cost:,.2f} logistics deduction. "
                    pros.append(f"Subsidized pickup (₹{transport_cost:.2f} deduction)")
                else:
                    explanation += f"Requires self-transport or carrier (estimated logistics deduction: ₹{transport_cost:,.2f}). "
                    cons.append(f"Self-transport required (₹{transport_cost:.2f} deduction)")

                if accepted_count == len(items):
                    pros.append("100% material compatibility (all items accepted)")
                elif accepted_count > 0:
                    cons.append(f"Only {accepted_count}/{len(items)} materials accepted at this facility")

                if compliance.cpcb_authorized:
                    pros.append("CPCB authorized facility with verified compliance")

                if fac.lead_time_hours <= 24:
                    pros.append(f"Fast dispatch lead time: {fac.lead_time_hours} hours")
                else:
                    cons.append(f"Lead time is {fac.lead_time_hours} hours")

            candidate = RecyclerMatchCandidate(
                rank=0,  # Will be assigned after sorting
                facility_id=str(fac.id),
                company_id=str(comp.id),
                company_name=comp.company_name,
                facility_name=fac.facility_name,
                city=fac.city,
                state=fac.state,
                compatibility_status=status,
                financial=financial,
                logistics=logistics,
                compliance=compliance,
                materials=mat_items,
                explanation=explanation,
                pros=pros,
                cons=cons,
            )
            candidates.append(candidate)

        # 10. Filter & Sort Candidates
        # Filter based on user query preferences
        eligible_candidates: List[RecyclerMatchCandidate] = []
        ineligible_candidates: List[RecyclerMatchCandidate] = []

        for c in candidates:
            if c.compatibility_status == "DISQUALIFIED_HAZARD":
                ineligible_candidates.append(c)
            elif require_pickup and not c.logistics.pickup_available:
                ineligible_candidates.append(c)
            elif max_distance_km and c.logistics.distance_km > max_distance_km:
                ineligible_candidates.append(c)
            elif c.compatibility_status == "INCOMPATIBLE_MATERIALS":
                ineligible_candidates.append(c)
            else:
                eligible_candidates.append(c)

        # Sort eligible candidates primarily by net_collector_earnings descending, secondarily by distance ascending
        eligible_candidates.sort(
            key=lambda x: (
                1 if x.compatibility_status == "FULLY_COMPATIBLE" else 0,
                x.financial.net_collector_earnings,
                -x.logistics.distance_km,
            ),
            reverse=True,
        )

        # Sort ineligible candidates by distance
        ineligible_candidates.sort(key=lambda x: x.logistics.distance_km)

        # Reassign Ranks
        ranked_list = eligible_candidates + ineligible_candidates
        for i, c in enumerate(ranked_list):
            c.rank = i + 1

        best_match = eligible_candidates[0] if eligible_candidates else None

        origin_coords = None
        if origin_lat is not None and origin_lon is not None:
            origin_coords = {"latitude": origin_lat, "longitude": origin_lon}

        return LotMatchingResponse(
            lot_id=lot_id,
            total_weight_kg=round(total_weight_kg, 3),
            has_hazardous_items=has_hazardous_items,
            origin_coordinates=origin_coords,
            total_candidates_evaluated=len(candidates),
            eligible_matches_count=len(eligible_candidates),
            best_match=best_match,
            recommendations=ranked_list,
        )


matching_service = MatchingService()
