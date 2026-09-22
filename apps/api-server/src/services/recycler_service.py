import uuid
from decimal import Decimal
from datetime import datetime, timezone
from typing import Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import AppException, ConflictError, ForbiddenError, NotFoundError, ValidationError
from ..models.user import User
from ..models.taxonomy import Material
from ..models.recycler import (
    RecyclerCompany,
    RecyclerFacility,
    AuthorizationRecord,
    RecyclerAcceptedMaterial,
    RecyclerServiceArea,
)
from ..schemas.recycler import (
    RegisterRecyclerRequest,
    UpdateRecyclerCompanyRequest,
    CreateFacilityRequest,
    UpdateFacilityRequest,
    CreateAuthorizationRequest,
    AuthorizationResponse,
    ConfigureAcceptedMaterialRequest,
    UpdateAcceptedMaterialRateRequest,
    AcceptedMaterialResponse,
    CreateServiceAreaRequest,
    ServiceAreaResponse,
    UpdatePickupAvailabilityRequest,
    PickupAvailabilityResponse,
    VerifyRecyclerRequest,
    VerificationStatusResponse,
    FacilityResponse,
    RecyclerCompanyResponse,
    RecyclerDirectoryItemResponse,
    RecyclerDirectoryListResponse,
)


class RecyclerService:
    """Manages verified recycler onboarding, facilities, authorizations, rates, and discovery."""

    @staticmethod
    def _map_authorization(auth: AuthorizationRecord) -> AuthorizationResponse:
        return AuthorizationResponse(
            id=str(auth.id),
            facility_id=str(auth.facility_id),
            authority_name=auth.authority_name,
            permit_type=auth.permit_type,
            permit_number=auth.permit_number,
            authorized_capacity_mta=float(auth.authorized_capacity_mta) if auth.authorized_capacity_mta else None,
            issued_date=auth.issued_date.isoformat(),
            expiry_date=auth.expiry_date.isoformat(),
            status=auth.status,
            document_url=auth.document_url,
            verified_at=auth.verified_at.isoformat() if auth.verified_at else None,
            created_at=auth.created_at.isoformat(),
        )

    @staticmethod
    def _map_material(acc: RecyclerAcceptedMaterial) -> AcceptedMaterialResponse:
        return AcceptedMaterialResponse(
            id=str(acc.id),
            facility_id=str(acc.facility_id),
            material_id=str(acc.material_id),
            material_name=acc.material.name if acc.material else "Unknown Material",
            material_code=acc.material.code if acc.material else "UNKNOWN",
            base_unit=acc.material.base_unit if acc.material else "KG",
            standard_rate_per_unit=float(acc.standard_rate_per_unit),
            minimum_accepted_weight_kg=float(acc.minimum_accepted_weight_kg),
            currency=acc.currency,
            is_active=acc.is_active,
        )

    @staticmethod
    def _map_service_area(area: RecyclerServiceArea) -> ServiceAreaResponse:
        return ServiceAreaResponse(
            id=str(area.id),
            facility_id=str(area.facility_id),
            region_name=area.region_name,
            state=area.state,
            city=area.city,
            postal_codes=area.postal_codes,
            radius_km=float(area.radius_km) if area.radius_km is not None else None,
            is_active=area.is_active,
        )

    def _map_facility(self, fac: RecyclerFacility) -> FacilityResponse:
        auth_responses = [self._map_authorization(a) for a in (fac.authorizations or [])]
        mat_responses = [self._map_material(m) for m in (fac.accepted_materials or [])]
        area_responses = [self._map_service_area(s) for s in (fac.service_areas or [])]

        return FacilityResponse(
            id=str(fac.id),
            recycler_id=str(fac.recycler_id),
            facility_name=fac.facility_name,
            address_line1=fac.address_line1,
            address_line2=fac.address_line2,
            city=fac.city,
            state=fac.state,
            postal_code=fac.postal_code,
            latitude=float(fac.latitude),
            longitude=float(fac.longitude),
            daily_capacity_kg=float(fac.daily_capacity_kg),
            accepts_hazardous=fac.accepts_hazardous,
            is_active=fac.is_active,
            pickup_available=fac.pickup_available,
            min_pickup_weight_kg=float(fac.min_pickup_weight_kg),
            max_pickup_distance_km=float(fac.max_pickup_distance_km),
            lead_time_hours=fac.lead_time_hours,
            pickup_operating_days=fac.pickup_operating_days,
            authorizations=auth_responses,
            accepted_materials=mat_responses,
            service_areas=area_responses,
        )

    def _map_company(self, comp: RecyclerCompany) -> RecyclerCompanyResponse:
        facilities = [self._map_facility(f) for f in (comp.facilities or [])]
        return RecyclerCompanyResponse(
            id=str(comp.id),
            user_id=str(comp.user_id),
            company_name=comp.company_name,
            trade_license_number=comp.trade_license_number,
            gst_number=comp.gst_number,
            cpcb_registration_no=comp.cpcb_registration_no,
            contact_person=comp.contact_person,
            contact_phone=comp.contact_phone,
            contact_email=comp.contact_email,
            operating_status=comp.operating_status,
            verification_notes=comp.verification_notes,
            verified_at=comp.verified_at.isoformat() if comp.verified_at else None,
            created_at=comp.created_at.isoformat(),
            facilities=facilities,
        )

    async def register_recycler(
        self,
        db: AsyncSession,
        user: User,
        data: RegisterRecyclerRequest,
    ) -> RecyclerCompanyResponse:
        """Register a new recycler company and its initial primary facility."""
        # Check if user already registered a company
        existing_user_comp = await db.execute(
            select(RecyclerCompany).where(RecyclerCompany.user_id == user.id)
        )
        if existing_user_comp.scalar_one_or_none():
            raise ConflictError(message="A recycler company is already registered for this user account")

        # Check unique constraints
        existing_cpcb = await db.execute(
            select(RecyclerCompany).where(RecyclerCompany.cpcb_registration_no == data.cpcb_registration_no.strip())
        )
        if existing_cpcb.scalar_one_or_none():
            raise ConflictError(message="A recycler with this CPCB registration number already exists")

        existing_license = await db.execute(
            select(RecyclerCompany).where(RecyclerCompany.trade_license_number == data.trade_license_number.strip())
        )
        if existing_license.scalar_one_or_none():
            raise ConflictError(message="A recycler with this trade license number already exists")

        if data.gst_number and data.gst_number.strip():
            existing_gst = await db.execute(
                select(RecyclerCompany).where(RecyclerCompany.gst_number == data.gst_number.strip())
            )
            if existing_gst.scalar_one_or_none():
                raise ConflictError(message="A recycler with this GST number already exists")

        # Upgrade user role to RECYCLER_ADMIN if currently COLLECTOR
        if user.role != "RECYCLER_ADMIN":
            user.role = "RECYCLER_ADMIN"
            db.add(user)

        # Create Recycler Company
        company = RecyclerCompany(
            user_id=user.id,
            company_name=data.company_name.strip(),
            trade_license_number=data.trade_license_number.strip(),
            gst_number=data.gst_number.strip() if data.gst_number else None,
            cpcb_registration_no=data.cpcb_registration_no.strip(),
            contact_person=data.contact_person.strip(),
            contact_phone=data.contact_phone.strip(),
            contact_email=data.contact_email.strip() if data.contact_email else None,
            operating_status="PENDING_VERIFICATION",
        )
        db.add(company)
        await db.flush()

        # Create Primary Facility
        pf = data.primary_facility
        facility = RecyclerFacility(
            recycler_id=company.id,
            facility_name=pf.facility_name.strip(),
            address_line1=pf.address_line1.strip(),
            address_line2=pf.address_line2.strip() if pf.address_line2 else None,
            city=pf.city.strip(),
            state=pf.state.strip(),
            postal_code=pf.postal_code.strip(),
            latitude=Decimal(str(round(pf.latitude, 8))),
            longitude=Decimal(str(round(pf.longitude, 8))),
            daily_capacity_kg=Decimal(str(round(pf.daily_capacity_kg, 2))),
            accepts_hazardous=pf.accepts_hazardous,
            pickup_available=pf.pickup_available,
            min_pickup_weight_kg=Decimal(str(round(pf.min_pickup_weight_kg, 2))),
            max_pickup_distance_km=Decimal(str(round(pf.max_pickup_distance_km, 2))),
            lead_time_hours=pf.lead_time_hours,
            pickup_operating_days=pf.pickup_operating_days.strip(),
            is_active=True,
        )
        db.add(facility)
        await db.commit()

        # Reload company with facilities
        return await self.get_recycler_profile(db, company.id)

    async def get_recycler_profile(
        self,
        db: AsyncSession,
        company_id: uuid.UUID,
    ) -> RecyclerCompanyResponse:
        """Fetch complete recycler company profile with all eager-loaded nested relationships."""
        result = await db.execute(
            select(RecyclerCompany)
            .where(RecyclerCompany.id == company_id)
            .options(
                selectinload(RecyclerCompany.facilities).selectinload(RecyclerFacility.authorizations),
                selectinload(RecyclerCompany.facilities).selectinload(RecyclerFacility.accepted_materials).selectinload(RecyclerAcceptedMaterial.material),
                selectinload(RecyclerCompany.facilities).selectinload(RecyclerFacility.service_areas),
            )
        )
        comp = result.scalar_one_or_none()
        if not comp:
            raise NotFoundError(message="Recycler company not found")
        return self._map_company(comp)

    async def get_recycler_by_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> RecyclerCompanyResponse:
        """Fetch current authenticated user's recycler company profile."""
        result = await db.execute(
            select(RecyclerCompany).where(RecyclerCompany.user_id == user_id)
        )
        comp = result.scalar_one_or_none()
        if not comp:
            raise NotFoundError(message="No recycler profile associated with this account")
        return await self.get_recycler_profile(db, comp.id)

    async def update_recycler_company(
        self,
        db: AsyncSession,
        user: User,
        data: UpdateRecyclerCompanyRequest,
    ) -> RecyclerCompanyResponse:
        """Update company profile details."""
        comp_res = await db.execute(
            select(RecyclerCompany).where(RecyclerCompany.user_id == user.id)
        )
        comp = comp_res.scalar_one_or_none()
        if not comp:
            raise NotFoundError(message="Recycler company not found for this user")

        if data.company_name is not None:
            comp.company_name = data.company_name.strip()
        if data.contact_person is not None:
            comp.contact_person = data.contact_person.strip()
        if data.contact_phone is not None:
            comp.contact_phone = data.contact_phone.strip()
        if data.contact_email is not None:
            comp.contact_email = data.contact_email.strip()
        if data.gst_number is not None:
            comp.gst_number = data.gst_number.strip() if data.gst_number else None

        await db.commit()
        return await self.get_recycler_profile(db, comp.id)

    async def add_facility(
        self,
        db: AsyncSession,
        user: User,
        data: CreateFacilityRequest,
    ) -> FacilityResponse:
        """Add a new processing facility to the recycler company."""
        comp_res = await db.execute(
            select(RecyclerCompany).where(RecyclerCompany.user_id == user.id)
        )
        comp = comp_res.scalar_one_or_none()
        if not comp:
            raise NotFoundError(message="Recycler company not found for this user")

        facility = RecyclerFacility(
            recycler_id=comp.id,
            facility_name=data.facility_name.strip(),
            address_line1=data.address_line1.strip(),
            address_line2=data.address_line2.strip() if data.address_line2 else None,
            city=data.city.strip(),
            state=data.state.strip(),
            postal_code=data.postal_code.strip(),
            latitude=Decimal(str(round(data.latitude, 8))),
            longitude=Decimal(str(round(data.longitude, 8))),
            daily_capacity_kg=Decimal(str(round(data.daily_capacity_kg, 2))),
            accepts_hazardous=data.accepts_hazardous,
            pickup_available=data.pickup_available,
            min_pickup_weight_kg=Decimal(str(round(data.min_pickup_weight_kg, 2))),
            max_pickup_distance_km=Decimal(str(round(data.max_pickup_distance_km, 2))),
            lead_time_hours=data.lead_time_hours,
            pickup_operating_days=data.pickup_operating_days.strip(),
            is_active=True,
        )
        db.add(facility)
        await db.commit()
        await db.refresh(facility)
        return self._map_facility(facility)

    async def add_authorization(
        self,
        db: AsyncSession,
        user: User,
        facility_id: str,
        data: CreateAuthorizationRequest,
    ) -> AuthorizationResponse:
        """Add a CPCB/SPCB regulatory permit to a facility."""
        try:
            fac_uuid = uuid.UUID(str(facility_id))
        except ValueError:
            raise ValidationError(message="Invalid facility ID format")

        fac_res = await db.execute(
            select(RecyclerFacility).where(RecyclerFacility.id == fac_uuid)
        )
        fac = fac_res.scalar_one_or_none()
        if not fac:
            raise NotFoundError(message="Facility not found")

        # Check existing permit number
        p_res = await db.execute(
            select(AuthorizationRecord).where(AuthorizationRecord.permit_number == data.permit_number.strip())
        )
        if p_res.scalar_one_or_none():
            raise ConflictError(message="Authorization permit with this number already exists")

        auth = AuthorizationRecord(
            facility_id=fac_uuid,
            authority_name=data.authority_name.strip(),
            permit_type=data.permit_type.strip(),
            permit_number=data.permit_number.strip(),
            authorized_capacity_mta=Decimal(str(round(data.authorized_capacity_mta, 2))) if data.authorized_capacity_mta else None,
            issued_date=data.issued_date,
            expiry_date=data.expiry_date,
            status=data.status.strip(),
            document_url=data.document_url.strip() if data.document_url else None,
        )
        db.add(auth)
        await db.commit()
        await db.refresh(auth)
        return self._map_authorization(auth)

    async def list_authorizations(
        self,
        db: AsyncSession,
        facility_id: str,
    ) -> List[AuthorizationResponse]:
        """List all authorizations for a facility."""
        try:
            fac_uuid = uuid.UUID(str(facility_id))
        except ValueError:
            raise ValidationError(message="Invalid facility ID format")

        res = await db.execute(
            select(AuthorizationRecord)
            .where(AuthorizationRecord.facility_id == fac_uuid)
            .order_by(AuthorizationRecord.expiry_date.desc())
        )
        records = res.scalars().all()
        return [self._map_authorization(a) for a in records]

    async def verify_recycler(
        self,
        db: AsyncSession,
        admin_user: User,
        company_id: str,
        data: VerifyRecyclerRequest,
    ) -> VerificationStatusResponse:
        """Admin action: verify, suspend, or reject recycler company."""
        try:
            comp_uuid = uuid.UUID(str(company_id))
        except ValueError:
            raise ValidationError(message="Invalid company ID format")

        comp_res = await db.execute(
            select(RecyclerCompany).where(RecyclerCompany.id == comp_uuid)
        )
        comp = comp_res.scalar_one_or_none()
        if not comp:
            raise NotFoundError(message="Recycler company not found")

        comp.operating_status = data.operating_status
        comp.verification_notes = data.verification_notes
        comp.verified_at = datetime.now(timezone.utc) if data.operating_status == "VERIFIED" else None
        comp.verified_by = admin_user.id if data.operating_status == "VERIFIED" else None

        await db.commit()
        await db.refresh(comp)

        return VerificationStatusResponse(
            company_id=str(comp.id),
            company_name=comp.company_name,
            operating_status=comp.operating_status,
            verification_notes=comp.verification_notes,
            verified_at=comp.verified_at.isoformat() if comp.verified_at else None,
        )

    async def configure_accepted_material(
        self,
        db: AsyncSession,
        user: User,
        facility_id: str,
        data: ConfigureAcceptedMaterialRequest,
    ) -> AcceptedMaterialResponse:
        """Configure accepted material and standing offered rate for a facility."""
        try:
            fac_uuid = uuid.UUID(str(facility_id))
            mat_uuid = uuid.UUID(str(data.material_id))
        except ValueError:
            raise ValidationError(message="Invalid UUID format for facility or material")

        # Verify facility
        fac_res = await db.execute(select(RecyclerFacility).where(RecyclerFacility.id == fac_uuid))
        if not fac_res.scalar_one_or_none():
            raise NotFoundError(message="Facility not found")

        # Verify material
        mat_res = await db.execute(select(Material).where(Material.id == mat_uuid))
        material = mat_res.scalar_one_or_none()
        if not material:
            raise NotFoundError(message="Material not found")

        # Check if already exists
        existing_res = await db.execute(
            select(RecyclerAcceptedMaterial).where(
                RecyclerAcceptedMaterial.facility_id == fac_uuid,
                RecyclerAcceptedMaterial.material_id == mat_uuid,
            )
        )
        existing = existing_res.scalar_one_or_none()

        if existing:
            existing.standard_rate_per_unit = Decimal(str(round(data.standard_rate_per_unit, 2)))
            existing.minimum_accepted_weight_kg = Decimal(str(round(data.minimum_accepted_weight_kg, 2)))
            existing.currency = data.currency.upper()
            existing.is_active = data.is_active
            db.add(existing)
            record = existing
        else:
            record = RecyclerAcceptedMaterial(
                facility_id=fac_uuid,
                material_id=mat_uuid,
                standard_rate_per_unit=Decimal(str(round(data.standard_rate_per_unit, 2))),
                minimum_accepted_weight_kg=Decimal(str(round(data.minimum_accepted_weight_kg, 2))),
                currency=data.currency.upper(),
                is_active=data.is_active,
            )
            db.add(record)

        await db.commit()
        await db.refresh(record)

        # Load relation
        record.material = material
        return self._map_material(record)

    async def list_accepted_materials(
        self,
        db: AsyncSession,
        facility_id: str,
    ) -> List[AcceptedMaterialResponse]:
        """List all accepted materials configured for a facility."""
        try:
            fac_uuid = uuid.UUID(str(facility_id))
        except ValueError:
            raise ValidationError(message="Invalid facility ID format")

        res = await db.execute(
            select(RecyclerAcceptedMaterial)
            .where(RecyclerAcceptedMaterial.facility_id == fac_uuid)
            .options(selectinload(RecyclerAcceptedMaterial.material))
        )
        records = res.scalars().all()
        return [self._map_material(m) for m in records]

    async def add_service_area(
        self,
        db: AsyncSession,
        user: User,
        facility_id: str,
        data: CreateServiceAreaRequest,
    ) -> ServiceAreaResponse:
        """Add a geographic service area to a facility."""
        try:
            fac_uuid = uuid.UUID(str(facility_id))
        except ValueError:
            raise ValidationError(message="Invalid facility ID format")

        fac_res = await db.execute(select(RecyclerFacility).where(RecyclerFacility.id == fac_uuid))
        if not fac_res.scalar_one_or_none():
            raise NotFoundError(message="Facility not found")

        area = RecyclerServiceArea(
            facility_id=fac_uuid,
            region_name=data.region_name.strip(),
            state=data.state.strip(),
            city=data.city.strip() if data.city else None,
            postal_codes=data.postal_codes.strip() if data.postal_codes else None,
            radius_km=Decimal(str(round(data.radius_km, 2))) if data.radius_km is not None else None,
            is_active=data.is_active,
        )
        db.add(area)
        await db.commit()
        await db.refresh(area)
        return self._map_service_area(area)

    async def list_service_areas(
        self,
        db: AsyncSession,
        facility_id: str,
    ) -> List[ServiceAreaResponse]:
        """List service areas for a facility."""
        try:
            fac_uuid = uuid.UUID(str(facility_id))
        except ValueError:
            raise ValidationError(message="Invalid facility ID format")

        res = await db.execute(
            select(RecyclerServiceArea).where(RecyclerServiceArea.facility_id == fac_uuid)
        )
        records = res.scalars().all()
        return [self._map_service_area(s) for s in records]

    async def update_pickup_availability(
        self,
        db: AsyncSession,
        user: User,
        facility_id: str,
        data: UpdatePickupAvailabilityRequest,
    ) -> PickupAvailabilityResponse:
        """Update pickup logistics configuration for a facility."""
        try:
            fac_uuid = uuid.UUID(str(facility_id))
        except ValueError:
            raise ValidationError(message="Invalid facility ID format")

        fac_res = await db.execute(select(RecyclerFacility).where(RecyclerFacility.id == fac_uuid))
        fac = fac_res.scalar_one_or_none()
        if not fac:
            raise NotFoundError(message="Facility not found")

        fac.pickup_available = data.pickup_available
        if data.min_pickup_weight_kg is not None:
            fac.min_pickup_weight_kg = Decimal(str(round(data.min_pickup_weight_kg, 2)))
        if data.max_pickup_distance_km is not None:
            fac.max_pickup_distance_km = Decimal(str(round(data.max_pickup_distance_km, 2)))
        if data.lead_time_hours is not None:
            fac.lead_time_hours = data.lead_time_hours
        if data.pickup_operating_days is not None:
            fac.pickup_operating_days = data.pickup_operating_days.strip()

        await db.commit()
        await db.refresh(fac)

        return PickupAvailabilityResponse(
            facility_id=str(fac.id),
            pickup_available=fac.pickup_available,
            min_pickup_weight_kg=float(fac.min_pickup_weight_kg),
            max_pickup_distance_km=float(fac.max_pickup_distance_km),
            lead_time_hours=fac.lead_time_hours,
            pickup_operating_days=fac.pickup_operating_days,
        )

    async def search_directory(
        self,
        db: AsyncSession,
        material_id: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        postal_code: Optional[str] = None,
        pickup_required: Optional[bool] = None,
        hazardous_required: Optional[bool] = None,
        verified_only: bool = True,
    ) -> RecyclerDirectoryListResponse:
        """Public / collector directory search for finding certified recyclers."""
        query = (
            select(RecyclerFacility)
            .join(RecyclerCompany, RecyclerFacility.recycler_id == RecyclerCompany.id)
            .options(
                selectinload(RecyclerFacility.company),
                selectinload(RecyclerFacility.authorizations),
                selectinload(RecyclerFacility.accepted_materials).selectinload(RecyclerAcceptedMaterial.material),
                selectinload(RecyclerFacility.service_areas),
            )
            .where(RecyclerFacility.is_active == True)
        )

        if verified_only:
            query = query.where(RecyclerCompany.operating_status == "VERIFIED")

        if pickup_required is True:
            query = query.where(RecyclerFacility.pickup_available == True)

        if hazardous_required is True:
            query = query.where(RecyclerFacility.accepts_hazardous == True)

        if city and city.strip():
            query = query.where(func.lower(RecyclerFacility.city) == city.strip().lower())

        if state and state.strip():
            query = query.where(func.lower(RecyclerFacility.state) == state.strip().lower())

        result = await db.execute(query)
        facilities = result.scalars().all()

        items: List[RecyclerDirectoryItemResponse] = []
        for f in facilities:
            # Filter by accepted material if requested
            if material_id:
                has_mat = any(
                    str(m.material_id) == material_id and m.is_active
                    for m in (f.accepted_materials or [])
                )
                if not has_mat:
                    continue

            # Build rate catalog
            rate_dict: Dict[str, float] = {}
            for m in (f.accepted_materials or []):
                if m.is_active and m.material:
                    rate_dict[m.material.code] = float(m.standard_rate_per_unit)

            regions = [s.region_name for s in (f.service_areas or []) if s.is_active]

            items.append(
                RecyclerDirectoryItemResponse(
                    facility_id=str(f.id),
                    company_id=str(f.company.id),
                    company_name=f.company.company_name,
                    facility_name=f.facility_name,
                    operating_status=f.company.operating_status,
                    city=f.city,
                    state=f.state,
                    postal_code=f.postal_code,
                    latitude=float(f.latitude),
                    longitude=float(f.longitude),
                    accepts_hazardous=f.accepts_hazardous,
                    pickup_available=f.pickup_available,
                    min_pickup_weight_kg=float(f.min_pickup_weight_kg),
                    lead_time_hours=f.lead_time_hours,
                    accepted_materials_count=len(f.accepted_materials or []),
                    active_authorizations_count=sum(
                        1 for a in (f.authorizations or []) if a.status == "ACTIVE"
                    ),
                    service_regions=regions,
                    rates=rate_dict,
                )
            )

        return RecyclerDirectoryListResponse(
            total=len(items),
            recyclers=items,
        )


recycler_service = RecyclerService()
