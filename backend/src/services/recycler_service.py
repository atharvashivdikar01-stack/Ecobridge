from sqlalchemy import select
from ..models import RecyclerCompany,RecyclerFacility
from ..core.exceptions import NotFoundError
class RecyclerService:
 async def register_recycler(self,db,user,data):
  c=RecyclerCompany(user_id=user.id,company_name=data.company_name,trade_license_number=data.trade_license_number,gst_number=data.gst_number,cpcb_registration_no=data.cpcb_registration_no,contact_person=data.contact_person,contact_phone=data.contact_phone); db.add(c); await db.flush(); return {'id':str(c.id),'company_name':c.company_name,'operating_status':c.operating_status}
 async def get_recycler_by_user(self,db,user_id):
  c=(await db.execute(select(RecyclerCompany).where(RecyclerCompany.user_id==user_id))).scalar_one_or_none();
  if not c: raise NotFoundError('Recycler company not found')
  return {'id':str(c.id),'company_name':c.company_name,'operating_status':c.operating_status}
 async def update_recycler_company(self,db,user,data): return await self.get_recycler_by_user(db,user.id)
 async def add_facility(self,db,user,data):
  c=(await db.execute(select(RecyclerCompany).where(RecyclerCompany.user_id==user.id))).scalar_one(); f=RecyclerFacility(recycler_id=c.id,**data.model_dump()); db.add(f); await db.flush(); return {'id':str(f.id),'facility_name':f.facility_name}
 async def add_authorization(self,*a,**k): return {}
 async def list_authorizations(self,*a,**k): return []
 async def verify_recycler(self,db,admin_user,company_id,data): return {}
 async def configure_accepted_material(self,*a,**k): return {}
 async def list_accepted_materials(self,*a,**k): return []
 async def add_service_area(self,*a,**k): return {}
 async def list_service_areas(self,*a,**k): return []
 async def update_pickup_availability(self,*a,**k): return {}
 async def search_directory(self,*a,**k): return {'recyclers':[]}
recycler_service=RecyclerService()
