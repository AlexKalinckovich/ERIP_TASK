--liquibase formatted sql

--changeset dev:001-create-exchange-rates
--comment: Create exchange_rates table storing NBRB rate history (idempotent source of truth)
CREATE TABLE exchange_rates (
    id            BIGINT       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rate_date     DATE         NOT NULL,
    currency_code VARCHAR(3)   NOT NULL,
    scale         INTEGER      NOT NULL DEFAULT 1,
    official_rate NUMERIC(12, 4) NOT NULL,
    created_at    TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_exchange_rates_date_currency UNIQUE (rate_date, currency_code),
    CONSTRAINT ck_exchange_rates_scale_positive CHECK (scale > 0),
    CONSTRAINT ck_exchange_rates_rate_positive  CHECK (official_rate > 0)
);
--rollback DROP TABLE exchange_rates;