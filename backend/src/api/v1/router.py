from fastapi import APIRouter
from .endpoints.health import router as health_router
from .endpoints.auth import router as auth_router
from .endpoints.collectors import router as collectors_router
from .endpoints.lots import router as lots_router
from .endpoints.pricing import router as pricing_router
from .endpoints.recyclers import router as recyclers_router
from .endpoints.matching import router as matching_router
from .endpoints.recycler_portal import router as recycler_portal_router
from .endpoints.sync import router as sync_router

v1_router = APIRouter()

# Register endpoint routers
v1_router.include_router(health_router)
v1_router.include_router(auth_router)
v1_router.include_router(collectors_router)
v1_router.include_router(lots_router)
v1_router.include_router(pricing_router)
v1_router.include_router(recyclers_router)
v1_router.include_router(matching_router)
v1_router.include_router(recycler_portal_router)
v1_router.include_router(sync_router)
