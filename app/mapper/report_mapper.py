from sqlalchemy import RowMapping

from app.schemas.report import SummaryReportItem


def map_db_row_to_summary_report_item(
    row : RowMapping
) -> SummaryReportItem:
    return SummaryReportItem(
        currency=row["currency"],
        total_received=row["total_received"],
        total_given=row["total_given"],
        deal_count=row["deal_count"],
    )