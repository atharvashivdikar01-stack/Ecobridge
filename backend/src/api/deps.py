from fastapi import Depends,Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db
from ..core.security import decode_token
from ..core.exceptions import UnauthorizedError,ForbiddenError
from ..models import User
async def get_current_user(authorization:str=Header(None),db:AsyncSession=Depends(get_db)):
 if not authorization or not authorization.lower().startswith('bearer '): raise UnauthorizedError()
 p=decode_token(authorization.split(' ',1)[1]); user=(await db.execute(select(User).where(User.id==p.get('sub')))).scalar_one_or_none()
 if not user or user.status!='ACTIVE': raise UnauthorizedError('User not found or inactive')
 return user
async def get_current_collector(user:User=Depends(get_current_user)):
 if user.role!='COLLECTOR': raise ForbiddenError('Collector access required')
 return user
async def get_current_recycler(user:User=Depends(get_current_user)):
 if user.role!='RECYCLER_ADMIN': raise ForbiddenError('Recycler access required')
 return user
async def get_current_admin(user:User=Depends(get_current_user)):
 if user.role!='ADMIN': raise ForbiddenError('Admin access required')
 return user
