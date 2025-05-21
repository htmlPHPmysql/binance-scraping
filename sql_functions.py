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

# --- Функція для підключення до бази даних ---
def get_db_connection():
    """
    Встановлює та повертає підключення до бази даних PostgreSQL.
    """
    connection = None
    try:
        connection = psycopg2.connect(
            user="postgres",
            password="3113325650", # !!! Ваш пароль
            host="127.0.0.1",
            port="5432",
            database="trading_data"
        )
        print(connection)
        return connection
        
    except (Exception, Error) as error:
        print(f"Помилка підключення до PostgreSQL: {error}")
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
    Створює таблицю 'traders_binance' у базі даних, якщо вона ще не існує.
    """
    
    cursor = connection.cursor()

    create_table_query = """
        CREATE TABLE IF NOT EXISTS traders_binance (
            id SERIAL PRIMARY KEY,
            trader_id VARCHAR(255) UNIQUE NOT NULL,
            profile_url TEXT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    cursor.execute(create_table_query)
    connection.commit() # Зберігаємо зміни (створення таблиці)

    # print("Таблиця 'traders_binance' перевірена/створена успішно.")

# --- Функція для додавання даних ---
def add_trader_data(connection, trader_id, profile_url):
    """
    Додає ID трейдера та посилання на його профіль у таблицю 'traders_binance'.
    """
    try:
        if connection is None:
            print("Не вдалося отримати підключення до бази даних для додавання даних. Вихід.")
            return
        else:
            # Creat new table if not exist
            create_traders_table(connection)

        cursor = connection.cursor()

        insert_query = """
        INSERT INTO traders_binance (trader_id, profile_url)
        VALUES (%s, %s);
        """
        cursor.execute(insert_query, (trader_id, profile_url))
        connection.commit() # Зберігаємо зміни (вставка даних)

        print(f"Дані для трейдера '{trader_id}' додано успішно.")

    except (Exception, Error) as error:
        # PGC0000 - це загальний SQLSTATE для унікального порушення
        # Можна перевіряти конкретніші коди помилок, наприклад, '23505' для unique_violation
        if isinstance(error, psycopg2.IntegrityError) and 'duplicate key value violates unique constraint' in str(error):
            print(f"Помилка: Трейдер з ID '{trader_id}' вже існує у базі даних. Пропускаємо.")
        else:
            print(f"Помилка при додаванні даних: {error}")

    finally:
        if connection:
            cursor.close()
            
