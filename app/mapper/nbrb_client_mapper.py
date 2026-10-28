from app.repositories.exchange_rate import RateRow
from app.schemas.nbrb import NBRBRate


def map_nbrb_rate_to_rate_row(nbrb_row: NBRBRate) -> RateRow:
    return RateRow(
        rate_date = nbrb_row.date.date(),
        currency_code = nbrb_row.cur_abbreviation,
        scale = nbrb_row.cur_scale,
        official_rate = nbrb_row.cur_official_rate,
    )