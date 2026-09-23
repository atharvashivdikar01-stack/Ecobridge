from contextlib import asynccontextmanager
from fastapi import FastAPI,Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.exceptions import AppException
from .core.bootstrap import bootstrap_database
from .api.v1.router import v1_router
import sys

@asynccontextmanager
async def lifespan(_app: FastAPI):
    if "pytest" not in sys.modules:
        await bootstrap_database()
    yield

app=FastAPI(title=settings.PROJECT_NAME,version=settings.VERSION,lifespan=lifespan)
Path(settings.MEDIA_ROOT).mkdir(parents=True, exist_ok=True)
app.mount('/media', StaticFiles(directory=settings.MEDIA_ROOT), name='media')
_origins = settings.CORS_ORIGINS or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials="*" not in _origins,
    allow_methods=['*'],
    allow_headers=['*'],
)
@app.exception_handler(AppException)
async def app_error(request:Request,exc:AppException): return JSONResponse(status_code=exc.status_code,content={'success':False,'error':{'code':exc.code,'message':exc.message,'details':exc.details}})
@app.exception_handler(Exception)
async def unhandled(request:Request,exc:Exception): return JSONResponse(status_code=500,content={'success':False,'error':{'code':'INTERNAL_ERROR','message':'Internal server error'}})
@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Request validation failed',
                'details': exc.errors(),
            },
        },
    )
app.include_router(v1_router,prefix=settings.API_V1_PREFIX)
