from app.db.models import Deal
from app.schemas.deal import (
    PendingDealItem
)

def map_deal_to_pending_item(deal : Deal) -> PendingDealItem:
    return PendingDealItem(
        deal_id=deal.deal_id,
        source_currency=deal.source_currency,
        target_currency=deal.target_currency,
        source_amount=deal.source_amount,
        target_amount=deal.target_amount,
        exchange_rate=deal.exchange_rate,
        created_at=deal.created_at,
    )