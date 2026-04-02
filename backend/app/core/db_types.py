"""Database type compatibility for SQLite and PostgreSQL."""
import json
import uuid

from sqlalchemy import String, Text, TypeDecorator


class GUID(TypeDecorator):
    """Platform-independent UUID type. Uses String(36) for SQLite."""
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return uuid.UUID(value)
        return value


class JSONType(TypeDecorator):
    """Platform-independent JSON type. Uses Text with JSON serialization for SQLite."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value, ensure_ascii=False)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        return value
