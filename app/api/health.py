from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/health", summary="Проверка работоспособности")
def health() -> dict[str, str]:
    return {"status": "ok"}
