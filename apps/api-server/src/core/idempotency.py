"""Small, storage-agnostic idempotency primitives for mutating endpoints."""
import hashlib
from dataclasses import dataclass


class IdempotencyConflict(ValueError):
    """The same key was reused with a different request."""


def request_fingerprint(actor: str, key: str, body: bytes) -> str:
    if not key or len(key) > 255:
        raise ValueError("Idempotency-Key must be between 1 and 255 characters")
    return hashlib.sha256(actor.encode() + b":" + key.encode() + b":" + body).hexdigest()


@dataclass
class IdempotencyRecord:
    fingerprint: str
    status_code: int
    response_body: bytes


class InMemoryIdempotencyStore:
    """Development-only store; production should use a transactional database/Redis store."""

    def __init__(self) -> None:
        self._records: dict[str, IdempotencyRecord] = {}

    def get_or_reserve(self, key: str, fingerprint: str) -> IdempotencyRecord | None:
        existing = self._records.get(key)
        if existing and existing.fingerprint != fingerprint:
            raise IdempotencyConflict("Idempotency-Key was reused for a different request")
        return existing

    def save(self, key: str, record: IdempotencyRecord) -> None:
        self._records[key] = record
