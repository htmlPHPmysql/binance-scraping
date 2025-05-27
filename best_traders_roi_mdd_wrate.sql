SELECT
    tpm.id,
    tpm.trader_id,
    tlt.trader_name, -- Додано ім'я трейдера
    tpm.period_days,
    tpm.pnl_value_sign,
    tpm.pnl_per_period,
    tpm.roi_per_period,
    tpm.mdd_per_period,
    tpm.win_rate_per_period,
    tpm.recorded_at
FROM
    trader_performance_metrics_test AS tpm
INNER JOIN
    trader_links_table AS tlt ON tpm.trader_id = tlt.trader_id -- Приєднання таблиці trader_links_table
WHERE
    tpm.roi_per_period > (SELECT AVG(roi_per_period) FROM trader_performance_metrics_test WHERE roi_per_period > 0) AND
    tpm.mdd_per_period < 5 AND
    tpm.win_rate_per_period > 95;