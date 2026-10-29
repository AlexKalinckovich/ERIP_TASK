--liquibase formatted sql
--changeset dev:006-create-deal-status-enum
CREATE TYPE deal_status_enum AS ENUM ('PENDING', 'CONFIRMED', 'REJECTED', 'EXPIRED');

DROP INDEX IF EXISTS idx_deals_pending_active;
DROP INDEX IF EXISTS idx_deals_summary_report;

ALTER TABLE deals ALTER COLUMN status DROP DEFAULT;

ALTER TABLE deals
    ALTER COLUMN status TYPE deal_status_enum
    USING status::deal_status_enum;

ALTER TABLE deals
    ALTER COLUMN status SET DEFAULT 'PENDING'::deal_status_enum;

ALTER TABLE deals DROP CONSTRAINT IF EXISTS ck_deals_status_valid;

CREATE INDEX idx_deals_pending_active
ON deals (created_at DESC)
WHERE status = 'PENDING'::deal_status_enum;

CREATE INDEX idx_deals_summary_report
ON deals (status, updated_at)
INCLUDE (source_currency, target_currency, source_amount, target_amount);

--rollback DROP INDEX IF EXISTS idx_deals_summary_report;
--rollback DROP INDEX IF EXISTS idx_deals_pending_active;
--rollback ALTER TABLE deals ADD CONSTRAINT ck_deals_status_valid CHECK (status::text IN ('PENDING', 'CONFIRMED', 'REJECTED', 'EXPIRED'));
--rollback ALTER TABLE deals ALTER COLUMN status SET DEFAULT 'PENDING';
--rollback ALTER TABLE deals ALTER COLUMN status TYPE VARCHAR(20) USING status::text::VARCHAR(20);
--rollback DROP TYPE deal_status_enum;