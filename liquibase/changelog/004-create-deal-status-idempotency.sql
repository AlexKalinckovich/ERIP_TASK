--liquibase formatted sql

--changeset dev:004-create-deal-status-idempotency
--comment: Store idempotent results for PATCH /api/v1/deals/{deal_id}
CREATE TABLE deal_status_idempotency_keys (
    idempotency_key UUID PRIMARY KEY,
    deal_id         UUID        NOT NULL,
    action          VARCHAR(10) NOT NULL,
    status          VARCHAR(20) NOT NULL,
    updated_at      TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_deal_status_idempotency_keys_deal
        FOREIGN KEY (deal_id) REFERENCES deals (deal_id) ON DELETE CASCADE,
    CONSTRAINT uq_deal_status_idempotency_keys_deal UNIQUE (deal_id),
    CONSTRAINT ck_deal_status_idempotency_keys_action
        CHECK (action IN ('CONFIRM', 'REJECT')),
    CONSTRAINT ck_deal_status_idempotency_keys_status
        CHECK (status IN ('CONFIRMED', 'REJECTED'))
);
--rollback DROP TABLE deal_status_idempotency_keys;
