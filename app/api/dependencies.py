from typing import Annotated

from fastapi import Depends

from app.services.deal_service import DealService
from app.services.deal_validator import DealValidator

def get_deal_validator() -> DealValidator:
    return DealValidator()

def get_deal_service(validator: Annotated[DealValidator, Depends(get_deal_validator)]) -> DealService:
    return DealService(validator=validator)
