from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....models import Lot, User
from ....schemas.lot import CreateLotRequest
from ....schemas.response import ApiResponse
from ....services.lot_service import lot_service
from ...deps import get_current_collector

router = APIRouter(prefix="/sync", tags=["Offline Sync"])


class Mutation(BaseModel):
    id: str = Field(min_length=1)
    lot_id: str = Field(min_length=1)
    record_type: str = Field(min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: str | None = None


class SyncBatch(BaseModel):
    mutations: list[Mutation] = Field(default_factory=list)
    client_id: str | None = None


@router.post("")
async def sync(
    batch: SyncBatch,
    collector: User = Depends(get_current_collector),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for mutation in batch.mutations:
        if mutation.record_type.lower() not in {"lot", "lot creation", "create_lot"}:
            results.append({"id": mutation.id, "status": "REJECTED", "message": "Unsupported mutation type"})
            continue
        existing = (
            await db.execute(
                select(Lot).where(
                    Lot.lot_code == mutation.lot_id,
                    Lot.collector_id == collector.collector_profile.id,
                )
            )
        ).scalar_one_or_none()
        if existing:
            results.append({"id": mutation.id, "lot_id": mutation.lot_id, "status": "SYNCHRONIZED", "duplicate": True})
            continue
        lot_data = CreateLotRequest.model_validate(mutation.payload)
        created = await lot_service.create_lot(db=db, collector_user=collector, data=lot_data)
        results.append({"id": mutation.id, "lot_id": created.id, "lot_code": created.lot_code, "status": "SYNCHRONIZED"})
    return ApiResponse.create_success({
        "synced_count": sum(1 for item in results if item["status"] == "SYNCHRONIZED"),
        "results": results,
        "server_time": datetime.now(timezone.utc).isoformat(),
    })
