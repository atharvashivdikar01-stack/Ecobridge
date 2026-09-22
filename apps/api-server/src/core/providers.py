"""Provider-neutral ports and safe development implementations.

Production integrations must be supplied by the deployment; the fallbacks never
pretend to deliver an OTP, charge a payment, or upload an object.
"""
from dataclasses import dataclass
from typing import Protocol


class ProviderUnavailable(RuntimeError):
    """Raised when a live provider has not been configured."""


class OtpProvider(Protocol):
    async def send(self, destination: str, code: str) -> str: ...


class PaymentProvider(Protocol):
    async def create_payment(self, amount: int, currency: str, reference: str) -> str: ...


class StorageProvider(Protocol):
    async def put(self, key: str, content: bytes, content_type: str) -> str: ...


@dataclass(frozen=True)
class DevelopmentOtpProvider:
    """Records no message and makes the non-delivery explicit."""

    async def send(self, destination: str, code: str) -> str:
        raise ProviderUnavailable("OTP provider is not configured for this environment")


@dataclass(frozen=True)
class DevelopmentPaymentProvider:
    async def create_payment(self, amount: int, currency: str, reference: str) -> str:
        raise ProviderUnavailable("Payment provider is not configured for this environment")


@dataclass(frozen=True)
class DevelopmentStorageProvider:
    async def put(self, key: str, content: bytes, content_type: str) -> str:
        raise ProviderUnavailable("Object storage provider is not configured for this environment")
