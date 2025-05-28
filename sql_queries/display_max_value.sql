SELECT
	id,
	trader_id,
	difference
FROM
    public.trading_data_per_days_test
WHERE
    difference IS NOT NULL  -- Виключаємо рядки, де difference є NULL
ORDER BY
    difference DESC
LIMIT 1;
