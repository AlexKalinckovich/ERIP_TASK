from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DealStatusIdempotency(Base):
    __tablename__ = "deal_status_idempotency_keys"
    __table_args__ = (
        CheckConstraint(
            "action IN ('CONFIRM', 'REJECT')",
            name="ck_deal_status_idempotency_keys_action",
        ),
        CheckConstraint(
            "status IN ('CONFIRMED', 'REJECTED')",
            name="ck_deal_status_idempotency_keys_status",
        ),
        UniqueConstraint(
            "deal_id",
            name="uq_deal_status_idempotency_keys_deal",
        ),
    )

    idempotency_key: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
    )
    deal_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("deals.deal_id", ondelete="CASCADE"),
        nullable=False,
    )
    action: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
