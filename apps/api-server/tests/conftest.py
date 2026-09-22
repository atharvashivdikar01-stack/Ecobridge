import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from src.main import app
from src.core.database import get_db
from src.core.exceptions import AppException, NotFoundError
from src.models import Base

# Setup isolated in-memory test database
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

TestSessionFactory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def override_get_db():
    async with TestSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Override application database dependency with test session
app.dependency_overrides[get_db] = override_get_db

# Create a test router to verify exception handling
test_router = APIRouter(prefix="/api/v1/test", tags=["Test Endpoints"])


class DummyInput(BaseModel):
    name: str
    amount: float


@test_router.post("/validate")
async def dummy_validate(data: DummyInput):
    return {"status": "ok", "name": data.name, "amount": data.amount}


@test_router.get("/app-exception")
async def dummy_app_exception():
    raise AppException(code="CUSTOM_ERROR", message="Test custom exception", status_code=400, details={"info": "extra"})


@test_router.get("/not-found")
async def dummy_not_found():
    raise NotFoundError("The requested test entity does not exist")


@test_router.get("/unhandled-error")
async def dummy_unhandled():
    raise RuntimeError("Intentional unhandled test error")


app.include_router(test_router)


@pytest_asyncio.fixture(autouse=True)
async def init_test_db():
    """Initializes tables before each test and drops them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    """Async test client with raise_app_exceptions=False."""
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
