class PriceIntelligenceService:
 async def get_material_price_intelligence(self,**k): return {'material_id':k['material_id'],'observations':[],'offers':[]}
 async def get_lot_valuation(self,**k): return {'lot_id':k['lot_id'],'estimated_value':0}
 async def record_observation(self,db,data): return data.model_dump()
 async def submit_recycler_offer(self,db,data): return data.model_dump()
price_intelligence_service=PriceIntelligenceService()
