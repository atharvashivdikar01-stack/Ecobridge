import uuid,hashlib
from datetime import datetime,timezone
from decimal import Decimal
from sqlalchemy import select,func
from sqlalchemy.orm import selectinload
from ..models import Lot,LotItem,LotImage,Material,MaterialPriceBand,WasteCategory,CustodyEvent
from ..models.collector import CollectorProfile
from ..core.exceptions import NotFoundError
from ..schemas.lot import *
class LotService:
 async def create_lot(self,db,collector_user,data):
  profile=collector_user.collector_profile
  if not profile: raise NotFoundError('Collector profile not found')
  now=data.offline_created_at or datetime.now(timezone.utc); lot=Lot(lot_code=data.lot_code or f'EB-{now:%Y%m}-{uuid.uuid4().hex[:4].upper()}',collector_id=profile.id,status='COLLECTED',offline_created_at=now,synced_at=datetime.now(timezone.utc),origin_latitude=data.origin_latitude,origin_longitude=data.origin_longitude,origin_address=data.origin_address)
  total=Decimal('0'); weight=Decimal('0'); db.add(lot); await db.flush()
  for i in data.items:
   mid=uuid.UUID(i.material_id); material=(await db.execute(select(Material).where(Material.id==mid))).scalar_one_or_none()
   if not material: raise NotFoundError('Material not found')
   band=(await db.execute(select(MaterialPriceBand).where(MaterialPriceBand.material_id==mid,MaterialPriceBand.is_active==True).order_by(MaterialPriceBand.effective_from.desc()))).scalars().first(); price=Decimal(str(i.unit_price_estimated if i.unit_price_estimated is not None else (band.benchmark_price_per_unit if band else 0))); subtotal=Decimal(str(i.estimated_weight_kg))*price; total+=subtotal; weight+=Decimal(str(i.estimated_weight_kg)); db.add(LotItem(lot_id=lot.id,material_id=mid,quantity=i.quantity,unit=i.unit,estimated_weight_kg=i.estimated_weight_kg,unit_price_estimated=price,subtotal_estimated=subtotal,detected_hazard=i.detected_hazard,ai_confidence_score=i.ai_confidence_score,notes=i.notes))
  lot.total_estimated_weight_kg=weight; lot.estimated_value=total
  for im in data.images or []:
   image_hash=im.image_hash or hashlib.sha256(im.image_url.encode('utf-8')).hexdigest()
   db.add(LotImage(lot_id=lot.id,image_url=im.image_url,image_hash=image_hash,captured_at=im.captured_at or now,latitude=im.latitude,longitude=im.longitude,is_proof_of_collection=im.is_proof_of_collection))
  db.add(CustodyEvent(lot_id=lot.id,sequence_number=1,event_type='CREATION',actor_id=collector_user.id,actor_role=collector_user.role,event_timestamp=now,event_payload_json={'lot_code':lot.lot_code},previous_event_hash='0'*64,current_event_hash=hashlib.sha256(f'{lot.id}CREATION'.encode()).hexdigest()))
  await db.flush()
  return await self._response(db, lot.id)
 async def _response(self,db,lot_id):
  result=await db.execute(select(Lot).where(Lot.id==lot_id).options(selectinload(Lot.collector).selectinload(CollectorProfile.user),selectinload(Lot.items).selectinload(LotItem.material).selectinload(Material.category),selectinload(Lot.images)))
  lot=result.scalar_one()
  return LotResponse(id=str(lot.id),lot_code=lot.lot_code,collector_id=str(lot.collector_id),collector_name=lot.collector.user.full_name,status=lot.status,total_estimated_weight_kg=float(lot.total_estimated_weight_kg),total_verified_weight_kg=float(lot.total_verified_weight_kg) if lot.total_verified_weight_kg else None,estimated_value=float(lot.estimated_value),final_value=float(lot.final_value) if lot.final_value else None,currency=lot.currency,origin_latitude=float(lot.origin_latitude) if lot.origin_latitude else None,origin_longitude=float(lot.origin_longitude) if lot.origin_longitude else None,origin_address=lot.origin_address,offline_created_at=lot.offline_created_at.isoformat(),synced_at=lot.synced_at.isoformat() if lot.synced_at else None,created_at=lot.created_at.isoformat(),items_count=len(lot.items),items=[LotItemResponse(id=str(i.id),material_id=str(i.material_id),material_name=i.material.name,material_code=i.material.code,category_name=i.material.category.name,quantity=i.quantity,unit=i.unit,estimated_weight_kg=float(i.estimated_weight_kg),verified_weight_kg=float(i.verified_weight_kg) if i.verified_weight_kg else None,unit_price_estimated=float(i.unit_price_estimated),subtotal_estimated=float(i.subtotal_estimated),detected_hazard=i.detected_hazard,ai_confidence_score=float(i.ai_confidence_score) if i.ai_confidence_score else None,notes=i.notes) for i in lot.items],images=[LotImageResponse(id=str(x.id),image_url=x.image_url,image_hash=x.image_hash,latitude=float(x.latitude) if x.latitude else None,longitude=float(x.longitude) if x.longitude else None,captured_at=x.captured_at.isoformat(),is_proof_of_collection=x.is_proof_of_collection) for x in lot.images])
 async def get_lot(self,db,lot_id_or_code,current_user):
  try: q=select(Lot).where(Lot.id==uuid.UUID(lot_id_or_code))
  except ValueError:q=select(Lot).where(Lot.lot_code==lot_id_or_code)
  lot=(await db.execute(q)).scalar_one_or_none()
  if not lot: raise NotFoundError('Lot not found')
  return await self._response(db, lot.id)
 async def list_collector_lots(self,db,current_user,status=None,page=1,page_size=20):
  q=select(Lot).where(Lot.collector_id==current_user.collector_profile.id); q=q.where(Lot.status==status) if status else q; lots=(await db.execute(q.order_by(Lot.created_at.desc()))).scalars().all(); return LotListResponse(lots=[await self._response(db,x.id) for x in lots[(page-1)*page_size:page*page_size]],total=len(lots),page=page,page_size=page_size)
 async def attach_image(self,db,lot_id_or_code,current_user,image_data):
  lot=(await db.execute(select(Lot).where(Lot.id==uuid.UUID(lot_id_or_code)))).scalar_one_or_none();
  if not lot: raise NotFoundError('Lot not found')
  image_hash=image_data.image_hash or hashlib.sha256(image_data.image_url.encode('utf-8')).hexdigest()
  im=LotImage(lot_id=lot.id,image_url=image_data.image_url,image_hash=image_hash,captured_at=image_data.captured_at or datetime.now(timezone.utc),latitude=image_data.latitude,longitude=image_data.longitude,is_proof_of_collection=image_data.is_proof_of_collection); db.add(im); await db.flush(); return LotImageResponse(id=str(im.id),image_url=im.image_url,image_hash=im.image_hash,latitude=im.latitude,longitude=im.longitude,captured_at=im.captured_at.isoformat(),is_proof_of_collection=im.is_proof_of_collection)
 async def get_active_taxonomy(self,db):
  cats=(await db.execute(select(WasteCategory).order_by(WasteCategory.code))).scalars().all(); out=[]
  for c in cats:
   mats=[]
   for m in c.materials:
    b=m.price_bands[0] if m.price_bands else None; mats.append(MaterialItemTaxonomy(id=str(m.id),code=m.code,name=m.name,base_unit=m.base_unit,benchmark_price_per_unit=float(b.benchmark_price_per_unit if b else 0),min_price_per_unit=float(b.min_price_per_unit if b else 0),max_price_per_unit=float(b.max_price_per_unit if b else 0),default_hazard=c.default_hazard))
   out.append(CategoryTaxonomyResponse(id=str(c.id),code=c.code,name=c.name,description=c.description,materials=mats))
  return TaxonomyListResponse(categories=out)
lot_service=LotService()
