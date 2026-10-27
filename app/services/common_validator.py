from uuid import UUID

from app.core.exceptions import InvalidUUIDError


def parse_uuid_or_raise(value: str, field: str = "id") -> UUID:
    try:
        return UUID(value)
    except ValueError as exc:
        raise InvalidUUIDError(field=field) from exc
