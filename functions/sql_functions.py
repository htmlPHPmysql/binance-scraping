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
        return connection
        
    except (Exception, Error) as error:
        print(f"Error connecting to PostgreSQL: {error}")
        return None
    
def db_close_connection(connection):
    """
    Closes the PostgreSQL database connection.
    """
    try:
        if connection:
            connection.close()
            print("Connection to PostgreSQL successfully closed")
        else:
            print("Connection to PostgreSQL does NOT exist")
    except (Exception, Error) as error:
        print(f"Error disconnecting from PostgreSQL: {error}")

def create_table(connection, table_name, columns):
    """
    Check if the table in the database exists and creates it if NOT exists.
    Allows dynamic definition of table name and columns.

    Parameters:
    connection (psycopg2.connection): Connection object to PostgreSQL database.
    table_name (str): Name of the table to check/create.
    columns (list): A list of dictionaries, where each dictionary defines a column.
                    Example: [{'name': 'id', 'type': 'SERIAL PRIMARY KEY'},
                              {'name': 'trader_id', 'type': 'VARCHAR(255) NOT NULL'}]
    """
    try:
        with connection.cursor() as cur:
            # Створюємо рядки для визначення стовпців
            column_definitions = []
            for col in columns:
                col_name = col['name']
                col_type = col['type']
                column_definitions.append(f"{col_name} {col_type}")
            
            # Об'єднуємо всі визначення стовпців комами
            columns_sql = ",\n                ".join(column_definitions)
            
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {columns_sql}
            );
            """
            
            cur.execute(create_table_query)
            connection.commit()
            print(f"Table '{table_name}' checked/created successfully")

    except Error as e:
        print(f"Помилка при перевірці або створенні таблиці '{table_name}': {e}")
        connection.rollback()

def create_trading_data_per_days(connection, table_name="trading_data_per_days"):
    """
    Check if the table in the data base exists and creats it if NOT exists

    Parameters:
    conconnectionn (psycopg2.connection): Connection object to date base PostgreSQL.
    table_name (str): Name of the table to check.
    """
    try:
        with connection.cursor() as cur:
            
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
            connection.commit()
            print(f"Table '{table_name}' checked/created successfully")

    except Error as e:
        print(f"Помилка при перевірці або створенні таблиці '{table_name}': {e}")
        # Важливо: Якщо виникла помилка, відкотіть транзакцію
        connection.rollback()

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


def insert_multiple_trader_links_batch(connection, table_name, data_list: list[tuple]):
    cursor = None
    try:
        if not data_list: return
        cursor = connection.cursor()
        insert_query = f"""
        INSERT INTO {table_name} (trader_id, trader_name, avatar_url)
        VALUES (%s, %s, %s)
        ON CONFLICT (trader_id) DO UPDATE SET
            trader_name = EXCLUDED.trader_name,
            avatar_url = EXCLUDED.avatar_url,
            recorded_at = CURRENT_TIMESTAMP;
        """
        cursor.executemany(insert_query, data_list)
        connection.commit()
        print(f"Successfully added/updated {len(data_list)} trader links in batch.")
    except (Exception, Error) as error:
        print(f"Error inserting/updating trader links in batch: {error}")
        if connection: connection.rollback()
    finally:
        if cursor: cursor.close()

def insert_multiple_batch(connection, table_name, table_columns, data_list: list[tuple]):
    try:
        if not data_list: return
        with connection.cursor() as cur:
            
            # 1. Відфільтруйте стовпці, щоб виключити 'id' та 'recorded_at' (якщо воно також генерується автоматично)
            # Зверніть увагу: для `recorded_at` з `DEFAULT CURRENT_TIMESTAMP` ви також не повинні його вказувати явно.
            # Тому ми відфільтруємо обидва стовпці.
            columns_to_insert_obj = [
                col for col in table_columns
                if col["name"] not in ["id", "recorded_at"]
            ]

            # 2. Отримайте тільки назви стовпців для INSERT частини запиту
            column_names = [col["name"] for col in columns_to_insert_obj]
            columns_str = ", ".join(column_names)

            # 3. Згенеруйте плейсхолдери (%s) для динамічної вставки
            placeholders = ", ".join(['%s'] * len(column_names))

            insert_query = f"""
                INSERT INTO {table_name} (
                    {columns_str}
                ) VALUES ({placeholders});
                """
