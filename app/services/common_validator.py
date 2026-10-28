from uuid import UUID

from app.core.exceptions import InvalidUUIDError


def parse_uuid_or_raise(
    value: str,
    field: str = "id",
    location: str = "path",
    version: int | None = None,
) -> UUID:
    try:
        parsed = UUID(value)
    except ValueError as exc:
        raise InvalidUUIDError(field=field, location=location) from exc

    if version is not None and parsed.version != version:
        raise InvalidUUIDError(
            field=field,
            message=f"UUID должен быть версии {version}.",
            location=location,
            error_type="uuid_version",
        )

    return parsed
