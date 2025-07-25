# config_sql.py

none = 0

trader_data_table_name = "trader_data"
trader_data_table_columns = [
        {"name": "id", "type": "SERIAL PRIMARY KEY"},
        {"name": "trader_id", "type": "VARCHAR(255) UNIQUE NOT NULL"},
        {"name": "trader_name", "type": "VARCHAR(255) NOT NULL"},
        {"name": "avatar_url", "type": "TEXT NOT NULL"},
        {"name": "recorded_at", "type": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"}
    ]

trader_metrics_table_name = "trader_metrics"
trader_metrics_table_columns = [
        {"name": "id", "type": "SERIAL PRIMARY KEY"},
        {"name": "trader_id", "type": "VARCHAR(255) NOT NULL"},
        {"name": "active_followers", "type": "INTEGER"},
        {"name": "total_spots", "type": "INTEGER"},
        {"name": "api_availability", "type": "VARCHAR(255)"},
        {"name": "aum_value", "type": "NUMERIC"},
        {"name": "sharpe_ratio_value", "type": "NUMERIC"},
        {"name": "portfolio_type", "type": "VARCHAR(255)"},
        {"name": "badge_name", "type": "VARCHAR(255)"},
        {"name": "recorded_at", "type": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"}
    ]

trader_performance_table_name = "trader_performance"
trader_performance_table_columns = [
        {"name": "id", "type": "SERIAL PRIMARY KEY"},
        {"name": "trader_id", "type": "VARCHAR(255) NOT NULL"},
        {"name": "period_days", "type": "INTEGER"},
        {"name": "pnl_per_period", "type": "NUMERIC"},
        {"name": "roi_per_period", "type": "NUMERIC"},
        {"name": "mdd_per_period", "type": "NUMERIC"},
        {"name": "win_rate_per_period", "type": "NUMERIC"},
        {"name": "recorded_at", "type": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"}
    ]