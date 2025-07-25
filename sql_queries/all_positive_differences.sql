SELECT
    tdpd.trader_id,
	tlt.trader_name,
    COUNT(*) AS positive_difference_count
FROM
    trading_data_per_days_test as tdpd
INNER JOIN
    trader_links_table AS tlt ON tdpd.trader_id = tlt.trader_id -- Приєднання таблиці trader_links_table
WHERE
    difference > 0 -- Фільтруємо лише додатні значення
GROUP BY
    tdpd.trader_id,
	tlt.trader_name
ORDER BY
    positive_difference_count DESC;