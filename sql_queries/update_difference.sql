---
WITH CalculatedNextValue AS (
    SELECT
        id,
        trader_id,
        value,
        date_time,
        -- Отримуємо значення 'value' з НАСТУПНОГО рядка для того ж трейдера,
        -- відсортовані за часом.
        LEAD(value, 1) OVER (PARTITION BY trader_id ORDER BY date_time ASC) AS next_value_for_this_row
    FROM
        public.trading_data_per_days_test
)
UPDATE public.trading_data_per_days_test AS tpd -- Таблиця, яку ми оновлюємо
SET
    -- Встановлюємо difference як 'value' наступного рядка мінус 'value' поточного рядка
    difference = cnd.next_value_for_this_row - cnd.value
FROM
    CalculatedNextValue AS cnd
WHERE
    tpd.id = cnd.id; -- З'єднуємо з CTE за id