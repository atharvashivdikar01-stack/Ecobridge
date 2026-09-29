import hashlib
import json
from datetime import datetime, timezone
import uuid
from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.lot import Lot
from ..models.traceability import CustodyEvent


class CustodyService:
    """Centralized service managing tamper-evident lot transitions and SHA-256 custody events."""

    @staticmethod
    def calculate_event_hash(
        previous_hash: str,
        lot_id: uuid.UUID,
        actor_id: Optional[uuid.UUID],
        event_type: str,
        payload: dict[str, Any],
    ) -> str:
        serialized_payload = json.dumps(payload, sort_keys=True, default=str)
        content = f"{previous_hash}:{lot_id}:{actor_id}:{event_type}:{serialized_payload}".encode("utf-8")
        return hashlib.sha256(content).hexdigest()

    async def record_transition(
        self,
        db: AsyncSession,
        lot: Lot,
        new_status: str,
        event_type: str,
        actor_id: Optional[uuid.UUID],
        actor_role: Optional[str],
        payload: dict[str, Any],
        timestamp: Optional[datetime] = None,
    ) -> CustodyEvent:
        """
        Transitions the lot status and appends a cryptographically verified CustodyEvent
        in the exact same database transaction.
        """
        ts = timestamp or datetime.now(timezone.utc)

        # Retrieve prior custody events to preserve the hash chain
        events = (
            await db.execute(
                select(CustodyEvent)
                .where(CustodyEvent.lot_id == lot.id)
                .order_by(CustodyEvent.sequence_number.asc())
            )
        ).scalars().all()

        previous_hash = events[-1].current_event_hash if events else "0" * 64
        sequence_number = len(events) + 1

        current_hash = self.calculate_event_hash(
            previous_hash=previous_hash,
            lot_id=lot.id,
            actor_id=actor_id,
            event_type=event_type,
            payload=payload,
        )

        event = CustodyEvent(
            lot_id=lot.id,
            sequence_number=sequence_number,
            event_type=event_type,
            actor_id=actor_id,
            actor_role=actor_role,
            event_timestamp=ts,
            event_payload_json=payload,
            previous_event_hash=previous_hash,
            current_event_hash=current_hash,
        )
        db.add(event)
        lot.status = new_status
        await db.flush()
        return event


custody_service = CustodyService()
