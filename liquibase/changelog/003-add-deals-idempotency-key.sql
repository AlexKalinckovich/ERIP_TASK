--liquibase formatted sql

--changeset dev:003-add-deals-idempotency-key
--comment: Add optional idempotency key for safe deal creation retries
ALTER TABLE deals ADD COLUMN idempotency_key UUID NULL;
CREATE UNIQUE INDEX uq_deals_idempotency_key
    ON deals (idempotency_key)
    WHERE idempotency_key IS NOT NULL;
--rollback DROP INDEX uq_deals_idempotency_key;
--rollback ALTER TABLE deals DROP COLUMN idempotency_key;
