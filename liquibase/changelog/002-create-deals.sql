--liquibase formatted sql

--changeset dev:002-create-deals
--comment: Create deals table for two-stage exchange lifecycle
CREATE TABLE deals (
    deal_id         UUID          PRIMARY KEY,
    source_currency VARCHAR(3)    NOT NULL,
    target_currency VARCHAR(3)    NOT NULL,
    source_amount   NUMERIC(15, 2) NOT NULL,
    target_amount   NUMERIC(15, 2) NOT NULL,
    exchange_rate   NUMERIC(12, 4) NOT NULL,
    status          VARCHAR(20)   NOT NULL DEFAULT 'PENDING',
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_deals_source_amount_positive CHECK (source_amount > 0),
    CONSTRAINT ck_deals_target_amount_positive CHECK (target_amount > 0),
    CONSTRAINT ck_deals_currencies_different  CHECK (source_currency <> target_currency),
    CONSTRAINT ck_deals_status_valid          CHECK (status IN ('PENDING', 'CONFIRMED', 'REJECTED', 'EXPIRED'))
);
--rollback DROP TABLE deals;

--changeset dev:002-create-deals-pending-idx
--comment: Partial index for GET /api/v1/deals/pending
CREATE INDEX idx_deals_pending_active
    ON deals (created_at DESC)
    WHERE status = 'PENDING';
--rollback DROP INDEX idx_deals_pending_active;

--changeset dev:002-create-deals-summary-idx
--comment: Covering index for GET /api/v1/deals/reports/summary (Index Only Scan)
CREATE INDEX idx_deals_summary_report
    ON deals (status, updated_at)
    INCLUDE (source_currency, target_currency, source_amount, target_amount);
--rollback DROP INDEX idx_deals_summary_report;