from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter,Depends
from sqlalchemy import text
from ....core.database import get_db
router=APIRouter()
@router.get('/health')
async def health_check(db:AsyncSession=Depends(get_db)):
 try: await db.execute(text('SELECT 1')); return {'status':'ok','database':'connected'}
 except Exception as e: return {'status':'error','database':'disconnected','detail':str(e)}
