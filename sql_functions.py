# sql_functions.py

import psycopg2
from psycopg2 import Error
# from credential_postgre import (
#     user,
#     password,
#     host,
#     port,
#     database
# )

# --- Data base connection function ---
def get_db_connection():
    """
    Establishes and returns a PostgreSQL database connection.
    """
    connection = None
    try:
        connection = psycopg2.connect(
            user="postgres",
            password="3113325650",
            host="127.0.0.1",
            port="5432",
            database="trading_data"
        )
        connection.autocommit = False # We'll manage transactions manually for batching
        print(f"Connection to PostgreSQL successfully established \n{connection}")
        return connection
        
    except (Exception, Error) as error:
        print(f"Error connecting to PostgreSQL: {error}")
        return None
    
def db_close_connection(connection):
    try:
        connection.close()
        print("Connection to PostgreSQL successfully closed")
    except (Exception, Error) as error:
        print(f"Помилка відключення від PostgreSQL: {error}")

# --- Функція для створення таблиці ---
def create_traders_table(connection):
    """
    
    """
    cursor = None
    try:
        cursor = connection.cursor()

        create_table_query = """
            CREATE TABLE IF NOT EXISTS trader_links_table (
                id SERIAL PRIMARY KEY, -- New auto-incrementing sequential number
                trader_id VARCHAR(255) UNIQUE NOT NULL, -- Now unique, but not the primary key
                trader_name VARCHAR(255) NOT NULL,
                profile_url TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        cursor.execute(create_table_query)
        connection.commit() # Зберігаємо зміни (створення таблиці)
        print("Table 'create_traders_table' checked/created successfully.")
    except (Exception, Error) as error:
        print(f"Error creating/checking table 'trader_metrics_table': {error}")
    finally:
        if cursor:
            cursor.close()

    # print("Таблиця 'traders_binance' перевірена/створена успішно.")

def create_trader_metrics_table(connection):
    """
    Creates the 'trader_metrics_table' table in the database if it doesn't already exist.
    This table stores various metrics for trader profiles, allowing for multiple records
    per trader_id (e.g., historical snapshots).
    """
    cursor = None
    try:
        cursor = connection.cursor()

        # SQL query to create the table with specified constraints:
        # id as SERIAL PRIMARY KEY: Unique auto-incrementing ID for each metrics record.
        # trader_id: Not unique, allows multiple entries for the same trader.
        # recorded_at: Timestamp to record when the metrics were collected.
        create_table_query = """
        CREATE TABLE IF NOT EXISTS trader_metrics_table (
            id SERIAL PRIMARY KEY,
            trader_id VARCHAR(255) NOT NULL, -- trader_id can be repeated as requested
            active_followers INTEGER,
            total_spots INTEGER,
            api_availability VARCHAR(255),
            aum_value NUMERIC, -- Use NUMERIC for decimal numbers like AUM and Sharpe Ratio
            sharpe_ratio_value NUMERIC,
            mock_status VARCHAR(255),
            copy_capability VARCHAR(255),
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'trader_metrics_table' checked/created successfully.")
    except (Exception, Error) as error:
        print(f"Error creating/checking table 'trader_metrics_table': {error}")
    finally:
        if cursor:
            cursor.close()

def create_trader_performance_table(connection):
    """
    Creates the 'trader_performance_metrics' table in the database if it doesn't already exist.
    This table stores specific performance metrics for traders, allowing for multiple records
    per trader_id (e.g., historical snapshots for different periods).
    """
    cursor = None
    try:
        cursor = connection.cursor()

        # SQL query to create the table with specified constraints:
        # id as SERIAL PRIMARY KEY: Unique auto-incrementing ID for each performance record.
        # trader_id: Not unique, allows multiple entries for the same trader for different periods/snapshots.
        # recorded_at: Timestamp to record when these performance metrics were collected.
        create_table_query = """
        CREATE TABLE IF NOT EXISTS trader_performance_metrics (
            id SERIAL PRIMARY KEY,
            trader_id VARCHAR(255) NOT NULL,
            period_days INTEGER,
            pnl_value_sign VARCHAR(1),
            pnl_per_period NUMERIC,
            roi_value_sign VARCHAR(1),
            roi_per_period NUMERIC,
            mdd_per_period NUMERIC,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'trader_performance_metrics' checked/created successfully.")
    except (Exception, Error) as error:
        print(f"Error creating/checking table 'trader_performance_metrics': {error}")
    finally:
        if cursor:
            cursor.close()

# --- Функція для додавання даних ---
# def add_trader_data(connection, trader_id, profile_url):
#     """
#     Додає ID трейдера та посилання на його профіль у таблицю 'traders_binance'.
#     """
#     cursor = None # Ініціалізація cursor
#     try:
#         if connection is None:
#             print("Не вдалося отримати підключення до бази даних для додавання даних. Вихід.")
#             return
#         else:
#             # Creat new table if not exist
#             create_traders_table(connection)

#         cursor = connection.cursor()

#         insert_query = """
#         INSERT INTO traders_binance (trader_id, profile_url)
#         VALUES (%s, %s);
#         """
#         cursor.execute(insert_query, (trader_id, profile_url))
#         connection.commit() # Зберігаємо зміни (вставка даних)

#         print(f"Дані для трейдера '{trader_id}' додано успішно.")

#     except (Exception, Error) as error:
#         if isinstance(error, psycopg2.IntegrityError) and error.pgcode == '23505':
#             print(f"Помилка: Трейдер з ID '{trader_id}' вже існує у базі даних. Пропускаємо.")
#             connection.rollback() # !!! Додано: Відкат транзакції після помилки унікального ключа
#         else:
#             print(f"Помилка при додаванні даних: {error}")

#     finally:
#         if cursor:
#             cursor.close()

def insert_trader_link(connection, trader_id: str, trader_name: str, profile_url: str):
    """
    Inserts a new trader link record into the 'trader_links_table'.
    If a record with the same trader_id already exists, it will be updated.
    The 'id' (sequential number) is auto-generated by the database.
    """
    cursor = None
    try:
        if connection is None:
            print("Could not get database connection to insert data. Exiting.")
            return

        cursor = connection.cursor()
        insert_query = """
        INSERT INTO trader_links_table (trader_id, trader_name, profile_url)
        VALUES (%s, %s, %s)
        ON CONFLICT (trader_id) DO UPDATE SET
            trader_name = EXCLUDED.trader_name,
            profile_url = EXCLUDED.profile_url,
            added_at = CURRENT_TIMESTAMP;
        """
        cursor.execute(insert_query, (trader_id, trader_name, profile_url))
        connection.commit()
        # print(f"Trader link for '{trader_name}' (ID: {trader_id}) added/updated successfully.")
    except (Exception, Error) as error:
        print(f"Error inserting/updating trader link for '{trader_name}': {error}")
        if connection:
            connection.rollback()
    finally:
        if cursor:
            cursor.close()
            print(f"{cursor} is closed")

def insert_trader_metrics(connection, metrics_data: dict):
    """
    Inserts a new record of trader metrics into the 'trader_metrics_table'.
    New records are always inserted as trader_id is not unique in this table (it captures snapshots).
    """
    cursor = None
    try:
        if connection is None:
            print("Could not get database connection to insert data. Exiting.")
            return

        cursor = connection.cursor()
        insert_query = """
        INSERT INTO trader_metrics_table (
            trader_id, active_followers, total_spots, api_availability, 
            aum_value, sharpe_ratio_value, mock_status, copy_capability
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        
        # Prepare data for insertion, handling potential 'N/A' or missing keys
        # Convert numeric values to appropriate types, default to None if 'N/A' or missing
        trader_id_val = metrics_data.get('trader_id')
        active_followers_val = int(metrics_data.get('active_followers')) if str(metrics_data.get('active_followers')).isdigit() else None
        total_spots_val = int(metrics_data.get('total_spots')) if str(metrics_data.get('total_spots')).isdigit() else None
        api_availability_val = metrics_data.get('api_availability')
        
        # Clean and convert AUM value
        aum_raw = metrics_data.get('aum_value')
        aum_value_val = None
        if isinstance(aum_raw, str):
            cleaned_aum = aum_raw.replace(',', '')
            if cleaned_aum.replace('.', '', 1).isdigit(): # Check if it's a valid number after cleaning
                aum_value_val = float(cleaned_aum)

        # Clean and convert Sharpe Ratio value
        sharpe_raw = metrics_data.get('sharpe_ratio_value')
        sharpe_ratio_value_val = None
        if isinstance(sharpe_raw, str):
            cleaned_sharpe = sharpe_raw.replace('–', '').strip() # Remove the dash if present
            if cleaned_sharpe and cleaned_sharpe.replace('.', '', 1).isdigit():
                sharpe_ratio_value_val = float(cleaned_sharpe)
        
        mock_status_val = metrics_data.get('mock_status')
        copy_capability_val = metrics_data.get('copy_capability')

        data_to_insert = (
            trader_id_val,
            active_followers_val,
            total_spots_val,
            api_availability_val,
            aum_value_val,
            sharpe_ratio_value_val,
            mock_status_val,
            copy_capability_val
        )

        cursor.execute(insert_query, data_to_insert)
        connection.commit()
        # print(f"Metrics for trader '{trader_id_val}' recorded successfully.")

    except (Exception, Error) as error:
        print(f"Error inserting metrics for trader '{metrics_data.get('trader_id')}': {error}")
        if connection:
            connection.rollback()
    finally:
        if cursor:
            cursor.close()
            
def insert_trader_performance(connection, performance_data: dict):
    """
    Inserts a new record of trader performance metrics into the 'trader_performance_metrics' table.
    New records are always inserted as trader_id is not unique in this table (it captures snapshots).
    """
    cursor = None
    try:
        if connection is None:
            print("Could not get database connection to insert data. Exiting.")
            return

        cursor = connection.cursor()
        insert_query = """
        INSERT INTO trader_performance_metrics (
            trader_id, period_days, pnl_value_sign, pnl_per_period,
            roi_value_sign, roi_per_period, mdd_per_period
        ) VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        
        # Prepare data for insertion, handling potential 'N/A' or missing keys
        # Convert numeric values to appropriate types, default to None if 'N/A' or missing
        trader_id_val = performance_data.get('trader_id')
        period_days_val = int(performance_data.get('period_days')) if str(performance_data.get('period_days')).isdigit() else None
        pnl_value_sign_val = performance_data.get('pnl_value_sign')
        
        pnl_raw = performance_data.get('pnl_per_period')
        pnl_per_period_val = None
        if isinstance(pnl_raw, str):
            cleaned_pnl = pnl_raw.replace(',', '').replace('%', '')
            if cleaned_pnl.replace('.', '', 1).lstrip('-+').isdigit(): # Check if it's a valid number
                pnl_per_period_val = float(cleaned_pnl)

        roi_value_sign_val = performance_data.get('roi_value_sign')
        
        roi_raw = performance_data.get('roi_per_period')
        roi_per_period_val = None
        if isinstance(roi_raw, str):
            cleaned_roi = roi_raw.replace(',', '').replace('%', '')
            if cleaned_roi.replace('.', '', 1).lstrip('-+').isdigit():
                roi_per_period_val = float(cleaned_roi)

        mdd_raw = performance_data.get('mdd_per_period')
        mdd_per_period_val = None
        if isinstance(mdd_raw, str):
            cleaned_mdd = mdd_raw.replace('%', '')
            if cleaned_mdd.replace('.', '', 1).lstrip('-+').isdigit():
                mdd_per_period_val = float(cleaned_mdd)

        data_to_insert = (
            trader_id_val,
            period_days_val,
            pnl_value_sign_val,
            pnl_per_period_val,
            roi_value_sign_val,
            roi_per_period_val,
            mdd_per_period_val
        )

        cursor.execute(insert_query, data_to_insert)
        connection.commit()
        # print(f"Performance metrics for trader '{trader_id_val}' (Period: {period_days_val} days) recorded successfully.")

    except (Exception, Error) as error:
        print(f"Error inserting performance metrics for trader '{performance_data.get('trader_id')}': {error}")
        if connection:
            connection.rollback()
    finally:
        if cursor:
            cursor.close()
