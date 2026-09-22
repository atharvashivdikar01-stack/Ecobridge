class CollectorService:
 async def get_profile(self,db,user):
  p=user.collector_profile; return {'id':str(p.id),'user_id':str(user.id),'full_name':user.full_name,'phone':user.phone,'collector_type':p.collector_type,'trust_score':float(p.trust_score),'total_lots_collected':p.total_lots_collected,'total_weight_kg':float(p.total_weight_kg)}
 async def update_profile(self,db,user,update_data): return await self.get_profile(db,user)
 async def submit_kyc(self,db,user,kyc_data): return await self.get_profile(db,user)
 async def get_stats(self,db,user):
  p=user.collector_profile; return {'total_lots_collected':p.total_lots_collected,'total_weight_kg':float(p.total_weight_kg),'trust_score':float(p.trust_score)}
collector_service=CollectorService()
