import uuid
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
class GUID(TypeDecorator):
    impl=CHAR(36); cache_ok=True
    def load_dialect_impl(self,dialect): return dialect.type_descriptor(CHAR(36)) if dialect.name=='sqlite' else dialect.type_descriptor(UUID(as_uuid=True))
    def process_bind_param(self,value,dialect): return str(value) if value is not None else None
    def process_result_value(self,value,dialect): return uuid.UUID(value) if value is not None and not isinstance(value,uuid.UUID) else value
