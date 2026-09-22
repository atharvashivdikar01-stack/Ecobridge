from fastapi import APIRouter,Depends
from pydantic import BaseModel,Field
from sqlalchemy import select
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from ....core.database import get_db
from ....core.exceptions import ForbiddenError,ConflictError,NotFoundError
from ....models import User,RecyclerCompany,Lot,RecyclerPayment
from ....schemas.response import ApiResponse
from ...deps import get_current_recycler
router=APIRouter(prefix='/recycler-portal',tags=['Recycler Portal'])
class Accept(BaseModel): agreed_price_per_kg:float=Field(gt=0); notes:str|None=None
class Handover(BaseModel): weighbridge_slip_number:str; weighbridge_gross_kg:float; weighbridge_tare_kg:float; verified_weight_kg:float=Field(gt=0); scale_calibration_id:str
class Payment(BaseModel): payment_method:str; amount:float=Field(gt=0); gateway_reference:str; notes:str|None=None
async def company(db,user): return (await db.execute(select(RecyclerCompany).where(RecyclerCompany.user_id==user.id))).scalar_one_or_none()
async def lot(db,id):
 x=(await db.execute(select(Lot).where(Lot.id==id))).scalar_one_or_none()
 if not x: raise NotFoundError('Lot not found')
 return x
@router.get('/dashboard')
async def dashboard(user:User=Depends(get_current_recycler),db:AsyncSession=Depends(get_db)):
 c=await company(db,user); return ApiResponse.create_success({'company_name':c.company_name,'is_verified':c.operating_status=='VERIFIED','operating_status':c.operating_status})
@router.get('/materials')
async def materials(user=Depends(get_current_recycler),db:AsyncSession=Depends(get_db)):
 rows=(await db.execute(select(Lot).where(Lot.status=='COLLECTED'))).scalars().all(); return ApiResponse.create_success({'items':[{'lot_id':str(x.id),'lot_code':x.lot_code,'estimated_weight_kg':float(x.total_estimated_weight_kg),'ai_confidence_score':float(x.items[0].ai_confidence_score or 0) if x.items else 0} for x in rows]})
@router.post('/lots/{lot_id}/accept')
async def accept(lot_id:str,data:Accept,user=Depends(get_current_recycler),db:AsyncSession=Depends(get_db)):
 c=await company(db,user)
 if not c or c.operating_status!='VERIFIED': raise ForbiddenError('Only authorized and CPCB-verified recyclers can accept offers')
 x=await lot(db,lot_id)
 if x.status!='COLLECTED': raise ConflictError('Lot already accepted')
 x.status='ACCEPTED'; x.agreed_price_per_kg=Decimal(str(data.agreed_price_per_kg)); x.final_value=x.total_estimated_weight_kg*x.agreed_price_per_kg; await db.flush(); return ApiResponse.create_success({'status':x.status,'agreed_price_per_kg':float(x.agreed_price_per_kg),'final_value':float(x.final_value)})
@router.post('/lots/{lot_id}/handover')
async def handover(lot_id:str,data:Handover,user=Depends(get_current_recycler),db:AsyncSession=Depends(get_db)):
 x=await lot(db,lot_id); x.status='HANDED_OVER'; x.total_verified_weight_kg=Decimal(str(data.verified_weight_kg)); x.verified_weight_kg=x.total_verified_weight_kg; x.weighbridge_slip_number=data.weighbridge_slip_number; x.final_value=x.agreed_price_per_kg*x.total_verified_weight_kg; await db.flush(); return ApiResponse.create_success({'status':x.status,'verified_weight_kg':float(x.total_verified_weight_kg),'final_value':float(x.final_value)})
@router.post('/lots/{lot_id}/payment', status_code=201)
async def payment(lot_id:str,data:Payment,user=Depends(get_current_recycler),db:AsyncSession=Depends(get_db)):
 x=await lot(db,lot_id); c=await company(db,user); p=RecyclerPayment(lot_id=x.id,recycler_id=c.id,payment_method=data.payment_method,payment_status='PAID',total_amount=Decimal(str(data.amount)),gateway_reference=data.gateway_reference,weighbridge_slip=x.weighbridge_slip_number or '',custody_hash='payment-'+str(x.id)); db.add(p); x.status='SETTLED'; await db.flush(); return ApiResponse.create_success({'payment_method':p.payment_method,'payment_status':p.payment_status,'total_amount':float(p.total_amount),'weighbridge_slip':p.weighbridge_slip,'custody_hash':p.custody_hash})
@router.get('/ledger')
async def ledger(user=Depends(get_current_recycler),db:AsyncSession=Depends(get_db)):
 c=await company(db,user); ps=(await db.execute(select(RecyclerPayment).where(RecyclerPayment.recycler_id==c.id))).scalars().all(); tx=[]
 for p in ps:
  x=await lot(db,str(p.lot_id)); tx.append({'lot_id':str(x.id),'payment_method':p.payment_method,'verified_weight_kg':float(x.total_verified_weight_kg or 0),'agreed_price_per_kg':float(x.agreed_price_per_kg or 0),'total_amount':float(p.total_amount)})
 return ApiResponse.create_success({'total_transactions':len(tx),'total_volume_kg':sum(t['verified_weight_kg'] for t in tx),'total_disbursed_inr':sum(t['total_amount'] for t in tx),'transactions':tx})
