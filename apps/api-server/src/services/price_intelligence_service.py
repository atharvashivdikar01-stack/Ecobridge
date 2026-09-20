import math
import uuid
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import AppException, NotFoundError, ValidationError
from ..models.taxonomy import Material, MaterialPriceBand
from ..models.lot import Lot, LotItem
from ..models.pricing import PriceObservation, RecyclerOffer
from ..schemas.pricing import (
    CreatePriceObservationRequest,
    CreateRecyclerOfferRequest,
    ObservedPriceDetail,
    ObservedMetricsResponse,
    ModelEstimateResponse,
    RecyclerOfferDetail,
    RecyclerOffersResponse,
    MaterialPriceIntelligenceResponse,
    LotValuationItemResponse,
    LotValuationResponse,
)


class PriceIntelligenceService:
    """Calculates empirical market observed prices and statistical model estimates.
    
    Invariants:
    - Strictly and explicitly distinguishes observed prices (EMPIRICAL_OBSERVATIONS)
      from model estimates (STATISTICAL_MODEL_ESTIMATE).
    - No machine learning: uses deterministic statistical quantiles (median, IQR, weighted median).
    """

    @staticmethod
    def _calculate_percentile(sorted_values: List[float], percentile: float) -> float:
        """Calculate the p-th percentile using linear interpolation."""
        if not sorted_values:
            return 0.0
        n = len(sorted_values)
        if n == 1:
            return sorted_values[0]
        
        index = (percentile / 100.0) * (n - 1)
        lower_idx = math.floor(index)
        upper_idx = math.ceil(index)
        
        if lower_idx == upper_idx:
            return sorted_values[lower_idx]
        
        fraction = index - lower_idx
        return sorted_values[lower_idx] + fraction * (sorted_values[upper_idx] - sorted_values[lower_idx])

    @staticmethod
    def _calculate_median(sorted_values: List[float]) -> float:
        """Calculate the exact median of a sorted list."""
        if not sorted_values:
            return 0.0
        n = len(sorted_values)
        mid = n // 2
        if n % 2 == 1:
            return sorted_values[mid]
        return (sorted_values[mid - 1] + sorted_values[mid]) / 2.0

    @staticmethod
    def _calculate_weighted_median(items: List[Tuple[float, float]]) -> float:
        """Calculate weighted median given pairs of (price, weight)."""
        if not items:
            return 0.0
        # Sort by price ascending
        sorted_items = sorted(items, key=lambda x: x[0])
        total_weight = sum(w for _, w in sorted_items)
        if total_weight <= 0:
            return sorted_items[len(sorted_items) // 2][0]

        cumulative_weight = 0.0
        target = total_weight / 2.0
        for price, weight in sorted_items:
            cumulative_weight += weight
            if cumulative_weight >= target:
                return price
        return sorted_items[-1][0]

    async def record_observation(
        self,
        db: AsyncSession,
        data: CreatePriceObservationRequest,
    ) -> ObservedPriceDetail:
        """Record an empirical market transaction or scrap quote."""
        try:
            mat_uuid = uuid.UUID(str(data.material_id))
        except ValueError:
            raise ValidationError(message=f"Invalid material ID format: {data.material_id}")

        # Verify material exists
        mat_res = await db.execute(select(Material).where(Material.id == mat_uuid))
        material = mat_res.scalar_one_or_none()
        if not material:
            raise NotFoundError(message=f"Material with ID '{data.material_id}' not found")

        obs_time = data.observed_at or datetime.now(timezone.utc)

        obs = PriceObservation(
            material_id=mat_uuid,
            price_per_unit=Decimal(str(round(data.price_per_unit, 2))),
            currency=data.currency.upper(),
            unit=data.unit.upper(),
            source_type=data.source_type,
            source_name=data.source_name.strip(),
            region=data.region.strip(),
            observed_at=obs_time,
            confidence_weight=Decimal(str(round(data.confidence_weight, 2))),
        )
        db.add(obs)
        await db.commit()
        await db.refresh(obs)

        return ObservedPriceDetail(
            id=str(obs.id),
            price_per_unit=float(obs.price_per_unit),
            currency=obs.currency,
            unit=obs.unit,
            source_type=obs.source_type,
            source_name=obs.source_name,
            region=obs.region,
            observed_at=obs.observed_at.isoformat(),
            confidence_weight=float(obs.confidence_weight),
        )

    async def submit_recycler_offer(
        self,
        db: AsyncSession,
        data: CreateRecyclerOfferRequest,
    ) -> RecyclerOfferDetail:
        """Submit an active offer from a certified recycler for a material or specific lot."""
        mat_uuid: Optional[uuid.UUID] = None
        lot_uuid: Optional[uuid.UUID] = None

        if data.material_id:
            try:
                mat_uuid = uuid.UUID(str(data.material_id))
            except ValueError:
                raise ValidationError(message=f"Invalid material ID format: {data.material_id}")
            mat_res = await db.execute(select(Material).where(Material.id == mat_uuid))
            if not mat_res.scalar_one_or_none():
                raise NotFoundError(message=f"Material with ID '{data.material_id}' not found")

        if data.lot_id:
            try:
                lot_uuid = uuid.UUID(str(data.lot_id))
            except ValueError:
                raise ValidationError(message=f"Invalid lot ID format: {data.lot_id}")
            lot_res = await db.execute(select(Lot).where(Lot.id == lot_uuid))
            if not lot_res.scalar_one_or_none():
                raise NotFoundError(message=f"Lot with ID '{data.lot_id}' not found")

        if not mat_uuid and not lot_uuid:
            raise ValidationError(message="Offer must target either a material_id or a lot_id")

        try:
            rec_uuid = uuid.UUID(str(data.recycler_id))
        except ValueError:
            raise ValidationError(message=f"Invalid recycler ID format: {data.recycler_id}")

        net_earning = Decimal(str(round(data.offered_total_price - data.pickup_cost_deduction, 2)))
        if net_earning < Decimal("0.00"):
            net_earning = Decimal("0.00")

        exp_time = data.expires_at or (datetime.now(timezone.utc) + timedelta(days=2))

        offer = RecyclerOffer(
            lot_id=lot_uuid,
            material_id=mat_uuid,
            recycler_id=rec_uuid,
            recycler_name=data.recycler_name.strip(),
            offered_price_per_unit=Decimal(str(round(data.offered_price_per_unit, 2))),
            offered_total_price=Decimal(str(round(data.offered_total_price, 2))),
            pickup_cost_deduction=Decimal(str(round(data.pickup_cost_deduction, 2))),
            net_collector_earning=net_earning,
            currency=data.currency.upper(),
            status="OFFERED",
            expires_at=exp_time,
        )
        db.add(offer)
        await db.commit()
        await db.refresh(offer)

        return RecyclerOfferDetail(
            id=str(offer.id),
            recycler_id=str(offer.recycler_id),
            recycler_name=offer.recycler_name,
            offered_price_per_unit=float(offer.offered_price_per_unit),
            offered_total_price=float(offer.offered_total_price),
            pickup_cost_deduction=float(offer.pickup_cost_deduction),
            net_collector_earning=float(offer.net_collector_earning),
            currency=offer.currency,
            status=offer.status,
            expires_at=offer.expires_at.isoformat(),
            created_at=offer.created_at.isoformat(),
        )

    async def get_material_price_intelligence(
        self,
        db: AsyncSession,
        material_id: str,
        region: Optional[str] = None,
    ) -> MaterialPriceIntelligenceResponse:
        """Calculate market observed metrics, statistical model estimates, and recycler offers."""
        try:
            mat_uuid = uuid.UUID(str(material_id))
        except ValueError:
            raise ValidationError(message=f"Invalid material ID format: {material_id}")

        # 1. Fetch Material details
        mat_res = await db.execute(select(Material).where(Material.id == mat_uuid))
        material = mat_res.scalar_one_or_none()
        if not material:
            raise NotFoundError(message=f"Material with ID '{material_id}' not found")

        # 2. Query stored price observations
        obs_query = select(PriceObservation).where(PriceObservation.material_id == mat_uuid)
        if region and region.strip() and region.strip().lower() != "national":
            # Match specific region or national baseline
            obs_query = obs_query.where(
                PriceObservation.region.in_([region.strip(), "National"])
            )
        obs_query = obs_query.order_by(PriceObservation.observed_at.desc())

        obs_result = await db.execute(obs_query)
        observations = obs_result.scalars().all()

        # 3. Compute Observed Metrics (strictly empirical)
        obs_details: List[ObservedPriceDetail] = []
        raw_prices: List[float] = []
        weighted_prices: List[Tuple[float, float]] = []

        for o in observations:
            price = float(o.price_per_unit)
            raw_prices.append(price)
            weighted_prices.append((price, float(o.confidence_weight)))
            obs_details.append(
                ObservedPriceDetail(
                    id=str(o.id),
                    price_per_unit=price,
                    currency=o.currency,
                    unit=o.unit,
                    source_type=o.source_type,
                    source_name=o.source_name,
                    region=o.region,
                    observed_at=o.observed_at.isoformat(),
                    confidence_weight=float(o.confidence_weight),
                )
            )

        sample_size = len(raw_prices)
        sorted_prices = sorted(raw_prices)

        if sample_size > 0:
            market_min = round(min(sorted_prices), 2)
            market_max = round(max(sorted_prices), 2)
            local_median = round(self._calculate_median(sorted_prices), 2)
            mean_val = round(sum(sorted_prices) / sample_size, 2)
            latest_price = round(raw_prices[0], 2)  # Most recent observation
        else:
            market_min = None
            market_max = None
            local_median = None
            mean_val = None
            latest_price = None

        observed_metrics = ObservedMetricsResponse(
            data_type="EMPIRICAL_OBSERVATIONS",
            sample_size=sample_size,
            market_min=market_min,
            market_max=market_max,
            local_median=local_median,
            mean=mean_val,
            latest_price=latest_price,
            observations=obs_details,
        )

        # 4. Compute Statistical Model Estimate (non-ML, deterministic quantile / IQR)
        pb = next((p for p in material.price_bands if p.is_active), None) if material.price_bands else None
        if not pb:
            pb_res = await db.execute(
                select(MaterialPriceBand)
                .where(MaterialPriceBand.material_id == mat_uuid, MaterialPriceBand.is_active == True)
                .order_by(MaterialPriceBand.effective_from.desc())
            )
            pb = pb_res.scalars().first()

        benchmark = float(pb.benchmark_price_per_unit) if pb else 150.0
        mat_min = float(pb.min_price_per_unit) if pb else 100.0
        mat_max = float(pb.max_price_per_unit) if pb else 200.0


        if sample_size >= 3:
            # Deterministic Interquartile Range (IQR)
            q1 = self._calculate_percentile(sorted_prices, 25)
            q3 = self._calculate_percentile(sorted_prices, 75)
            fair = self._calculate_weighted_median(weighted_prices)
            
            # Floor is max of Q1 or 80% of fair price; Ceiling is min of Q3 or 120% of fair price
            floor_est = max(0.0, min(q1, fair * 0.90))
            ceil_est = max(q3, fair * 1.10)

            if sample_size >= 10:
                confidence = "HIGH"
            elif sample_size >= 5:
                confidence = "MEDIUM"
            else:
                confidence = "LOW"

            model_estimate = ModelEstimateResponse(
                data_type="STATISTICAL_MODEL_ESTIMATE",
                fair_price=round(fair, 2),
                recommended_floor=round(floor_est, 2),
                recommended_ceiling=round(ceil_est, 2),
                method="WEIGHTED_MEDIAN_IQR",
                confidence_level=confidence,
            )
        elif sample_size in (1, 2):
            # Sparse sample: anchor around observed median with wider variance
            fair = self._calculate_median(sorted_prices)
            model_estimate = ModelEstimateResponse(
                data_type="STATISTICAL_MODEL_ESTIMATE",
                fair_price=round(fair, 2),
                recommended_floor=round(fair * 0.85, 2),
                recommended_ceiling=round(fair * 1.15, 2),
                method="WEIGHTED_MEDIAN_IQR",
                confidence_level="LOW",
            )
        else:
            # 0 observations: fallback to official baseline benchmark price band
            model_estimate = ModelEstimateResponse(
                data_type="STATISTICAL_MODEL_ESTIMATE",
                fair_price=round(benchmark, 2),
                recommended_floor=round(mat_min, 2),
                recommended_ceiling=round(mat_max, 2),
                method="TAXONOMY_BENCHMARK_FALLBACK",
                confidence_level="INSUFFICIENT_DATA",
            )

        # 5. Query Active Recycler Offers
        now_utc = datetime.now(timezone.utc)
        offers_query = (
            select(RecyclerOffer)
            .where(
                RecyclerOffer.material_id == mat_uuid,
                RecyclerOffer.status == "OFFERED",
                RecyclerOffer.expires_at > now_utc,
            )
            .order_by(RecyclerOffer.offered_price_per_unit.desc())
        )
        offers_result = await db.execute(offers_query)
        offers_list = offers_result.scalars().all()

        offer_details: List[RecyclerOfferDetail] = []
        offer_prices: List[float] = []

        for off in offers_list:
            p = float(off.offered_price_per_unit)
            offer_prices.append(p)
            offer_details.append(
                RecyclerOfferDetail(
                    id=str(off.id),
                    recycler_id=str(off.recycler_id),
                    recycler_name=off.recycler_name,
                    offered_price_per_unit=p,
                    offered_total_price=float(off.offered_total_price),
                    pickup_cost_deduction=float(off.pickup_cost_deduction),
                    net_collector_earning=float(off.net_collector_earning),
                    currency=off.currency,
                    status=off.status,
                    expires_at=off.expires_at.isoformat(),
                    created_at=off.created_at.isoformat(),
                )
            )

        active_count = len(offer_details)
        highest_offer = round(max(offer_prices), 2) if active_count > 0 else None
        avg_offer = round(sum(offer_prices) / active_count, 2) if active_count > 0 else None

        active_recycler_offers = RecyclerOffersResponse(
            data_type="ACTIVE_RECYCLER_OFFERS",
            active_offers_count=active_count,
            highest_offer_price=highest_offer,
            average_offer_price=avg_offer,
            offers=offer_details,
        )

        return MaterialPriceIntelligenceResponse(
            material_id=str(material.id),
            material_code=material.code,
            material_name=material.name,
            base_unit=material.base_unit,
            region=region or "National",
            benchmark_price=benchmark,
            observed_metrics=observed_metrics,
            model_estimate=model_estimate,
            active_recycler_offers=active_recycler_offers,
        )

    async def get_lot_valuation(
        self,
        db: AsyncSession,
        lot_id: str,
    ) -> LotValuationResponse:
        """Calculate dynamic lot valuation by combining line items with current intelligence."""
        try:
            lot_uuid = uuid.UUID(str(lot_id))
        except ValueError:
            raise ValidationError(message=f"Invalid lot ID format: {lot_id}")

        lot_res = await db.execute(select(Lot).where(Lot.id == lot_uuid))
        lot = lot_res.scalar_one_or_none()
        if not lot:
            raise NotFoundError(message=f"Lot with ID '{lot_id}' not found")

        # Load lot items
        items_res = await db.execute(
            select(LotItem)
            .where(LotItem.lot_id == lot_uuid)
            .options(selectinload(LotItem.material))
        )
        items = items_res.scalars().all()

        total_weight = 0.0
        total_estimated_value = 0.0
        items_valuation: List[LotValuationItemResponse] = []
        min_est_total = 0.0
        max_est_total = 0.0

        for item in items:
            weight = float(item.estimated_weight_kg)
            total_weight += weight

            # Get price intelligence for item's material
            intel = await self.get_material_price_intelligence(db, str(item.material_id))

            observed_median = intel.observed_metrics.local_median
            model_rate = intel.model_estimate.fair_price or intel.benchmark_price
            floor_rate = intel.model_estimate.recommended_floor or (model_rate * 0.85)
            ceil_rate = intel.model_estimate.recommended_ceiling or (model_rate * 1.15)

            subtotal = round(weight * model_rate, 2)
            total_estimated_value += subtotal
            min_est_total += weight * floor_rate
            max_est_total += weight * ceil_rate

            items_valuation.append(
                LotValuationItemResponse(
                    material_id=str(item.material_id),
                    material_name=item.material.name if item.material else "Unknown",
                    weight_kg=weight,
                    observed_median_rate=observed_median,
                    estimated_model_rate=model_rate,
                    subtotal_estimated=subtotal,
                )
            )

        # Check for active offers specifically targeting this lot
        now_utc = datetime.now(timezone.utc)
        lot_offers_res = await db.execute(
            select(RecyclerOffer).where(
                RecyclerOffer.lot_id == lot_uuid,
                RecyclerOffer.status == "OFFERED",
                RecyclerOffer.expires_at > now_utc,
            )
        )
        lot_offers = lot_offers_res.scalars().all()
        highest_active_offer = (
            round(max(float(o.net_collector_earning) for o in lot_offers), 2)
            if lot_offers
            else None
        )

        return LotValuationResponse(
            lot_id=str(lot.id),
            total_weight_kg=round(total_weight, 3),
            currency=lot.currency,
            items_valuation=items_valuation,
            total_estimated_value=round(total_estimated_value, 2),
            highest_active_offer=highest_active_offer,
            model_estimate_range={
                "floor": round(min_est_total, 2),
                "fair": round(total_estimated_value, 2),
                "ceiling": round(max_est_total, 2),
            },
        )


price_intelligence_service = PriceIntelligenceService()
