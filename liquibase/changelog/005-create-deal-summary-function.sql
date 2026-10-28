--liquibase formatted sql
--changeset dev:005-create-deal-summary-function splitStatements:false
CREATE OR REPLACE FUNCTION get_deal_summary_report(
    p_date_from TIMESTAMP WITH TIME ZONE,
    p_date_to TIMESTAMP WITH TIME ZONE,
    p_currency VARCHAR(3) DEFAULT NULL
)
RETURNS TABLE (
    currency VARCHAR(3),
    total_received NUMERIC(15, 2),
    total_given NUMERIC(15, 2),
    deal_count BIGINT
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        currency,
        COALESCE(SUM(received_amount), 0.00)::NUMERIC(15, 2) AS total_received,
        COALESCE(SUM(given_amount), 0.00)::NUMERIC(15, 2) AS total_given,
        COUNT(*)::BIGINT AS deal_count
    FROM (
        SELECT
            source_currency AS currency,
            source_amount AS received_amount,
            0.00::NUMERIC(15, 2) AS given_amount
        FROM deals
        WHERE status = 'CONFIRMED'
          AND updated_at >= p_date_from
          AND updated_at <= p_date_to
          AND (p_currency IS NULL OR source_currency = UPPER(p_currency))

        UNION ALL

        SELECT
            target_currency AS currency,
            0.00::NUMERIC(15, 2) AS received_amount,
            target_amount AS given_amount
        FROM deals
        WHERE status = 'CONFIRMED'
          AND updated_at >= p_date_from
          AND updated_at <= p_date_to
          AND (p_currency IS NULL OR target_currency = UPPER(p_currency))
    ) AS combined_deals
    GROUP BY currency
    ORDER BY currency ASC;
$$;

--rollback DROP FUNCTION IF EXISTS get_deal_summary_report(TIMESTAMP WITH TIME ZONE, TIMESTAMP WITH TIME ZONE, VARCHAR);