from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    Index,
    Numeric,
    String,
    desc,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Deal(Base):
    __tablename__ = "deals"
    __table_args__ = (
        CheckConstraint(
            "source_amount > 0",
            name="ck_deals_source_amount_positive",
        ),
        CheckConstraint(
            "target_amount > 0",
            name="ck_deals_target_amount_positive",
        ),
        CheckConstraint(
            "source_currency <> target_currency",
            name="ck_deals_currencies_different",
        ),
        Index(
            "idx_deals_pending_active",
            desc("created_at"),
            postgresql_where=text("status = 'PENDING'::deal_status_enum"),
        ),
        Index(
            "idx_deals_summary_report",
            "status",
            "updated_at",
            postgresql_include=[
                "source_currency",
                "target_currency",
                "source_amount",
                "target_amount",
            ],
        ),
        Index(
            "uq_deals_idempotency_key",
            "idempotency_key",
            unique=True,
            postgresql_where=text("idempotency_key IS NOT NULL"),
        ),
    )

    deal_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    source_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    target_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    source_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    exchange_rate: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(
            "PENDING",
            "CONFIRMED",
            "REJECTED",
            "EXPIRED",
            name="deal_status_enum",
            create_type=False,
        ),
        nullable=False,
        server_default="PENDING",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    idempotency_key: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
    )