import requests
from requests.exceptions import ConnectionError, Timeout, HTTPError, RequestException
import psycopg2
from psycopg2 import Error
import time
import random # For random delays
from sql_functions import (
    # add_trader_data,
    get_db_connection,
    # create_traders_table,
    # create_trader_metrics_table,
    # create_trader_performance_table,
    # insert_trader_link,
    # insert_trader_metrics,
    # insert_trader_performance,
    # db_close_connection
) # Import SQL functions

from functions_api import (
    fetch_api_data_with_retries,
) # Import API functions

# Period is usually fixed for these leaderboards, e.g., 30 Days
period_days = '180' # Assuming fixed 30 Days based on your previous data

# --- Database Connection Functions (from previous discussions) ---

# def get_db_connection():
#     """
#     Establishes and returns a PostgreSQL database connection.
#     """
#     connection = None
#     try:
#         connection = psycopg2.connect(
#             user="postgres",
#             password="3113325650", # !!! REPLACE WITH YOUR ACTUAL PASSWORD !!!
#             host="127.0.0.1",
#             port="5432",
#             database="trading_data" # Ensure this database exists
#         )
#         connection.autocommit = False # We'll manage transactions manually for batching
#         print("Connection to PostgreSQL successfully established.")
#         return connection
        
#     except (Exception, Error) as error:
#         print(f"Error connecting to PostgreSQL: {error}")
#         return None

def db_close_connection(connection):
    """
    Closes the PostgreSQL database connection.
    """
    try:
        if connection:
            connection.close()
            print("Connection to PostgreSQL successfully closed.")
    except (Exception, Error) as error:
        print(f"Error disconnecting from PostgreSQL: {error}")

# --- Table Creation Functions (from previous discussions) ---

def create_trader_links_table(connection):
    cursor = None
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS trader_links_table (
            id SERIAL PRIMARY KEY,
            trader_id VARCHAR(255) UNIQUE NOT NULL,
            trader_name VARCHAR(255) NOT NULL,
            avatar_url TEXT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'trader_links_table' checked/created successfully.")
    except (Exception, Error) as error:
        print(f"Error creating/checking table 'trader_links_table': {error}")
        if connection: connection.rollback()
    finally:
        if cursor: cursor.close()

def create_trader_metrics_table(connection):
    cursor = None
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS trader_metrics_table (
            id SERIAL PRIMARY KEY,
            trader_id VARCHAR(255) NOT NULL,
            active_followers INTEGER,
            total_spots INTEGER,
            api_availability VARCHAR(255),
            aum_value NUMERIC,
            sharpe_ratio_value NUMERIC,
            portfolio_type VARCHAR(255),
            copy_capability VARCHAR(255),
            badge_name VARCHAR(255),
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'trader_metrics_table' checked/created successfully.")
    except (Exception, Error) as error:
        print(f"Error creating/checking table 'trader_metrics_table': {error}")
        if connection: connection.rollback()
    finally:
        if cursor: cursor.close()

def create_trader_performance_table(connection):
    cursor = None
    try:
        cursor = connection.cursor()
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
            win_rate_per_period NUMERIC,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'trader_performance_metrics' checked/created successfully.")
    except (Exception, Error) as error:
        print(f"Error creating/checking table 'trader_performance_metrics': {error}")
        if connection: connection.rollback()
    finally:
        if cursor: cursor.close()

# --- Batch Data Insertion Functions (as defined previously) ---

def create_trading_data_per_days(connection, table_name="trading_data_per_days"):
    """
    Перевіряє, чи існує таблиця в базі даних, і створює її, якщо не існує.

    Параметри:
    conn (psycopg2.connection): Об'єкт підключення до бази даних PostgreSQL.
    table_name (str): Ім'я таблиці, яку потрібно перевірити/створити.
    """
    try:
        with conn.cursor() as cur:
            # SQL-запит для створення таблиці, якщо вона не існує.
            # Використовуємо IF NOT EXISTS, щоб уникнути помилок, якщо таблиця вже є.
            #
            # Стовпці:
            # id:         PRIMARY KEY SERIAL для унікального ідентифікатора запису.
            # trader_id:  INTEGER, може бути неунікальним (NOT NULL, якщо він завжди має бути).
            # value:      NUMERIC для десяткових чисел.
            # data_type:  VARCHAR(50) для текстового типу даних (наприклад, 'ROI').
            # date_time:  BIGINT для міток часу Unix в мілісекундах.
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                trader_id VARCHAR(255) NOT NULL, -- Додаємо trader_id, який може бути неунікальним
                value NUMERIC(10, 4) NOT NULL, -- NUMERIC(precision, scale) для точності
                data_type VARCHAR(50) NOT NULL,
                date_time BIGINT NOT NULL,
                difference NUMERIC(10, 4)
            );
            """
            cur.execute(create_table_query)
            conn.commit()
            print(f"Таблиця '{table_name}' перевірена/створена успішно.")

    except Error as e:
        print(f"Помилка при перевірці або створенні таблиці '{table_name}': {e}")
        # Важливо: Якщо виникла помилка, відкотіть транзакцію
        conn.rollback()

def insert_multiple_trader_links_batch(connection, data_list: list[tuple]):
    cursor = None
    try:
        if not data_list: return
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO trader_links_table (trader_id, trader_name, avatar_url)
        VALUES (%s, %s, %s)
        ON CONFLICT (trader_id) DO UPDATE SET
            trader_name = EXCLUDED.trader_name,
            avatar_url = EXCLUDED.avatar_url,
            added_at = CURRENT_TIMESTAMP;
        """
        cursor.executemany(insert_query, data_list)
        connection.commit()
        print(f"Successfully added/updated {len(data_list)} trader links in batch.")
    except (Exception, Error) as error:
        print(f"Error inserting/updating trader links in batch: {error}")
        if connection: connection.rollback()
    finally:
        if cursor: cursor.close()

def insert_multiple_trader_metrics_batch(connection, data_list: list[tuple]):
    cursor = None
    try:
        if not data_list: return
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO trader_metrics_table (
            trader_id, active_followers, total_spots, api_availability, 
            aum_value, sharpe_ratio_value, portfolio_type, copy_capability, badge_name
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.executemany(insert_query, data_list)
        connection.commit()
        print(f"Successfully inserted {len(data_list)} trader metrics records in batch.")
    except (Exception, Error) as error:
        print(f"Error inserting trader metrics in batch: {error}")
        if connection: connection.rollback()
    finally:
        if cursor: cursor.close()

def insert_multiple_trader_performance_metrics_batch(connection, data_list: list[tuple]):
    cursor = None
    try:
        if not data_list: return
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO trader_performance_metrics (
            trader_id, period_days, pnl_value_sign, pnl_per_period,
            roi_value_sign, roi_per_period, mdd_per_period, win_rate_per_period
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.executemany(insert_query, data_list)
        connection.commit()
        print(f"Successfully inserted {len(data_list)} trader performance records in batch.")
    except (Exception, Error) as error:
        print(f"Error inserting trader performance metrics in batch: {error}")
        if connection: connection.rollback()
    finally:
        if cursor: cursor.close()

# 
def insert_trading_data(connection, data_list: list[tuple]):
    """
    Вставляє дані у таблицю trading_data.

    Параметри:
    connection (psycopg2.connection): Об'єкт підключення до бази даних PostgreSQL.
    data (dict): Словник з даними для вставки (value, dataType, dateTime, trader_id).
    table_name (str): Ім'я таблиці для вставки.
    """
    try:
        if not data_list: return
        cursor = connection.cursor()
        insert_query = """
            INSERT INTO trading_data_per_days (trader_id, value, data_type, date_time, difference)
            VALUES (%s, %s, %s, %s, %s);
            """
        cursor.executemany(insert_query, data_list)
        connection.commit()
        print(f"Successfully inserted {len(data_list)} days of trading in batch.")
            
    except (Exception, Error) as error:
        print(f"Error inserting trading data per date in batch: {error}")
        if connection: connection.rollback()
    finally:
        if cursor: cursor.close()

# --- Helper for data cleaning/conversion (shared logic for preparing data) ---

def clean_and_convert_numeric(value, target_type):
    """
    Cleans and converts a string value to a numeric type (int or float).
    Handles 'N/A', '–', commas, and percentage signs. Returns None on invalid input.
    """
    # If the value is already a number (from API response), return it directly
    if isinstance(value, (int, float)):
        return value

    if not isinstance(value, str):
        return None # Or handle as per your default for non-string, non-numeric

    cleaned_value = value.strip()
    cleaned_value = cleaned_value.replace(',', '').replace('%', '').replace('–', '')

    if not cleaned_value:
        return None
    
    try:
        if target_type == int:
            return int(float(cleaned_value)) # Convert to float first to handle decimals like '1.0'
        elif target_type == float:
            return float(cleaned_value)
    except ValueError:
        return None
    return None

# --- Function for parsing the JSON response ---

def parse_api_response_for_traders(json_data: dict) -> list[dict]:
    """
    Parses the JSON response from the API to extract trader data.
    Maps API fields to the dictionary structure expected by our database insertion functions.
    """
    traders_data = []
    # print(json_data)
    try:
        # Navigate the JSON structure to find the list of traders
        trader_list = json_data.get('data', {}).get('list', [])

        for item in trader_list:
            # Extract and map fields from the API response item
            trader_id = item.get('leadPortfolioId')
            name = item.get('nickname')
            
            # Use avatarUrl directly from the API response
            profile_avatar_url = item.get('avatarUrl') # Changed from 'link' to 'avatarUrl'
            
            active_followers = item.get('currentCopyCount')
            total_spots = item.get('maxCopyCount')
            
            # API availability: based on 'apiKeyTag' being null or not
            api_availability = item.get('apiKeyTag')

            # badgeName: based on 'badgeName' being null or not
            badge_name = item.get('badgeName')

            # PnL Value and Sign
            pnl_value = item.get('pnl')
            pnl_value_sign = '+' if pnl_value is not None and pnl_value >= 0 else '-'
            pnl_per_period = str(abs(pnl_value)) if pnl_value is not None else 'N/A'

            # ROI Value and Sign
            roi_value = item.get('roi')
            roi_value_sign = '+' if roi_value is not None and roi_value >= 0 else '-'
            roi_per_period = str(abs(roi_value)) if roi_value is not None else 'N/A'

            # AUM Value
            aum_value = str(item.get('aum', 'N/A'))

            # MDD Value (directly a float/decimal in API)
            mdd_value = item.get('mdd')
            mdd_per_period = str(mdd_value) if mdd_value is not None else 'N/A'

            win_rate = item.get('winRate')
            win_rate_per_period = str(win_rate) if win_rate is not None else 'N/A'

            # Sharpe Ratio Value (note the key 'sharpRatio' in JSON)
            sharpe_ratio_value = str(item.get('sharpRatio', 'N/A')) # Use 'N/A' if null/not present

            # Mock Status (based on 'portfolioType')
            portfolio_type = item.get('portfolioType')

            # ROI evety day
            chart_items = item.get('chartItems')
            
            # Copy Capability - as 'copyStatus' is not in the provided JSON, default to 'N/A'
            copy_capability = 'N/A' # Default to N/A as it's not present in sample JSON

            traders_data.append({
                'trader_id': trader_id,
                'name': name,
                'active_followers': active_followers,
                'total_spots': total_spots,
                'api_availability': api_availability,
                'period_days': period_days,
                'pnl_value_sign': pnl_value_sign,
                'pnl_per_period': pnl_per_period,
                'roi_value_sign': roi_value_sign,
                'roi_per_period': roi_per_period,
                'aum_value': aum_value,
                'mdd_per_period': mdd_per_period,
                'win_rate_per_period': win_rate_per_period,
                'sharpe_ratio_value': sharpe_ratio_value,
                'portfolioType': portfolio_type,
                'chartItems': chart_items,
                'copy_capability': copy_capability,
                'badgeName': badge_name,
                'avatarUrl': profile_avatar_url # Changed from 'link' to 'avatarUrl'
            })
    except (KeyError, TypeError) as e:
        print(f"Error parsing JSON response: Missing key or unexpected type - {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during JSON parsing: {e}")
        return []

    return traders_data


# --- Main Script Execution ---

if __name__ == "__main__":
    API_URL = "https://www.binance.com/bapi/futures/v1/friendly/future/copy-trade/home-page/query-list"
    
    TOTAL_ITEMS = 60
    PAGE_SIZE = 18    
    
    TOTAL_PAGES = (TOTAL_ITEMS + PAGE_SIZE - 1) // PAGE_SIZE
    print(TOTAL_PAGES)
    
    BATCH_SIZE = 50  

    conn = get_db_connection()
    if not conn:
        print("Exiting due to database connection error.")
        exit()

    try:
        # 1. Create all necessary tables first
        create_trader_links_table(conn)
        create_trader_metrics_table(conn)
        create_trader_performance_table(conn)
        create_trading_data_per_days(conn)
        
        trader_links_batch = []
        trader_metrics_batch = []
        trader_performance_batch = []

        print("\n--- Starting data scraping from API and insertion ---")

        for page_num in range(1, TOTAL_PAGES + 1):
            
            print(f"Fetching data for page {page_num}/{TOTAL_PAGES} from API with PAGE_SIZE={PAGE_SIZE}.")

            payload = {
                "pageNumber": page_num,
                "pageSize": PAGE_SIZE, 
                "timeRange": period_days + "D",
                "dataType": "PNL",
                "favoriteOnly": False,
                "hideFull": False,
                "nickname": "",
                "order": "DESC",
                "userAsset": 0,
                "portfolioType": "PUBLIC",
                "useAiRecommended": False
            }
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9,uk;q=0.8',
                'ClientType': 'web',
                'Referer': 'https://www.binance.com/copy-trading/leaderboard'
            }


            json_response_data = fetch_api_data_with_retries(API_URL, headers, payload, page_num, 5, 10)
            if json_response_data is None:
                print(f"Припиняю пагінацію, оскільки не вдалося отримати дані для сторінки {page_num}.")
                break # Виходимо з головного циклу пагінації

            try:
                traders_on_page = parse_api_response_for_traders(json_response_data)
                
                print(f"Received {len(traders_on_page)} traders on page {page_num}.")

                if not traders_on_page:
                    print(f"No traders found in API response for page {page_num}. Ending pagination.")
                    break

                for trader_data in traders_on_page:
                    # Use 'avatarUrl' instead of 'link' for trader_links_batch
                    trader_links_batch.append((
                        trader_data.get('trader_id'),
                        trader_data.get('name'),
                        trader_data.get('avatarUrl') # Changed to avatarUrl
                    ))

                    metrics_to_add = (
                        trader_data.get('trader_id'),
                        clean_and_convert_numeric(trader_data.get('active_followers'), int),
                        clean_and_convert_numeric(trader_data.get('total_spots'), int),
                        trader_data.get('api_availability'),
                        clean_and_convert_numeric(trader_data.get('aum_value'), float),
                        clean_and_convert_numeric(trader_data.get('sharpe_ratio_value'), float),
                        trader_data.get('portfolioType'),
                        trader_data.get('copy_capability'),
                        trader_data.get('badgeName'),
                        
                    )
                    trader_metrics_batch.append(metrics_to_add)

                    performance_to_add = (
                        trader_data.get('trader_id'),
                        clean_and_convert_numeric(trader_data.get('period_days'), int),
                        trader_data.get('pnl_value_sign'),
                        clean_and_convert_numeric(trader_data.get('pnl_per_period'), float),
                        trader_data.get('roi_value_sign'),
                        clean_and_convert_numeric(trader_data.get('roi_per_period'), float),
                        clean_and_convert_numeric(trader_data.get('mdd_per_period'), float),
                        clean_and_convert_numeric(trader_data.get('win_rate_per_period'), float)                        
                    )
                    
                    trader_performance_batch.append(performance_to_add)

                    chart_items_batch = []
                    chart_items = trader_data.get('chartItems')
                    for chart_item in chart_items:
                        
                        chart_item_to_add = (
                            trader_data.get('trader_id'),
                            chart_item.get('value'),
                            chart_item.get('dataType'),
                            chart_item.get('dateTime'),
                            null                        
                        )
                        chart_items_batch.append(chart_item_to_add)
                    # insert_trading_data(conn, chart_items_batch)
                        # print(chart_item_to_add)
                    # trading_per_date_batch = {
                    #     'trader_id' = trader_data.get('trader_id')
                    # }
                    # trading_per_date_batch.append(trader_data.get('chartItems'))
                    # print(trading_per_date_batch)

                    # trading_per_date_to_add = (
                    #     trader_data.get('trader_id'),
                    #     clean_and_convert_numeric(trader_data.get('active_followers'), int),
                    #     clean_and_convert_numeric(trader_data.get('total_spots'), int),
                    #     trader_data.get('api_availability'),
                    #     clean_and_convert_numeric(trader_data.get('aum_value'), float),
                    #     clean_and_convert_numeric(trader_data.get('sharpe_ratio_value'), float),
                    #     trader_data.get('portfolioType'),
                    #     trader_data.get('copy_capability'),
                    #     trader_data.get('badgeName'),
                        
                    # )
                    

                    # insert_trading_data(connection, trading_per_date_batch)

                    if len(trader_links_batch) >= BATCH_SIZE:
                        print(f"Inserting batch of {len(trader_links_batch)} traders...")
                        insert_multiple_trader_links_batch(conn, trader_links_batch)
                        insert_multiple_trader_metrics_batch(conn, trader_metrics_batch)
                        insert_multiple_trader_performance_metrics_batch(conn, trader_performance_batch)
                        
                        trader_links_batch = []
                        trader_metrics_batch = []
                        trader_performance_batch = []

            except requests.exceptions.RequestException as e:
                print(f"Error fetching API data for page {page_num}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while processing API response for page {page_num}: {e}")
            
            sleep_time = random.uniform(1, 5)
            print(f"Waiting for {sleep_time:.2f} seconds before next API call...")
            time.sleep(sleep_time)

        if trader_links_batch:
            print(f"Inserting remaining batch of {len(trader_links_batch)} traders...")
            # insert_multiple_trader_links_batch(conn, trader_links_batch)
            # insert_multiple_trader_metrics_batch(conn, trader_metrics_batch)
            # insert_multiple_trader_performance_metrics_batch(conn, trader_performance_batch)

        print("\n--- Data scraping and insertion complete ---")

    except Exception as e:
        print(f"A critical error occurred during script execution: {e}")
    finally:
        db_close_connection(conn)
