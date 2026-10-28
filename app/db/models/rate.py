from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    Identity,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    __table_args__ = (
        UniqueConstraint(
            "rate_date",
            "currency_code",
            name="uq_exchange_rates_date_currency",
        ),
        CheckConstraint(
            "scale > 0",
            name="ck_exchange_rates_scale_positive",
        ),
        CheckConstraint(
            "official_rate > 0",
            name="ck_exchange_rates_rate_positive",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )
    rate_date: Mapped[date] = mapped_column(Date, nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    scale: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="1",
    )
    official_rate: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
