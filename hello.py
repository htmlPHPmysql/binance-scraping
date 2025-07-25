import re
import psycopg2  # For PostgreSQL
import os # Import module "os"
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from functions.selenium_functions import (
    close_popup_if_exists, 
    uncheck_checkbox, 
    check_element_presence, 
    wait_for_element_to_disappear,
    get_trader_links,
    extract_trader_id,
    # get_trader_details
)
from functions.sql_functions import (
    # add_trader_data,
    get_db_connection,
    create_traders_table,
    create_trader_metrics_table,
    create_trader_performance_table,
    insert_trader_link,
    insert_trader_metrics,
    insert_trader_performance,
    db_close_connection
)
from config import (
    URL,
    DATA_LOAD_TIMEOUT,
    OUTPUT_FILENAME,
    popup_class,
    close_button_class,
    checkbox_selector,
    pages_selector,
    name_trader_class,
    loading_indicator_class,
    TRADER_CARD_CLASS,
    SELECTOR_CLASSES
)
if __name__ == "__main__":
    # --- Code for Codespaces GitHub START ---
    # chromedriver_path = "/usr/local/bin/chromedriver" # Шлях до завантаженого вами ChromeDriver
    
    # chrome_options = Options()
    # chrome_options.add_argument("--headless") # Запускає Chrome без вікна (обов'язково для Codespaces)
    # chrome_options.add_argument("--no-sandbox") # Обов'язково для Codespaces/Docker
    # chrome_options.add_argument("--disable-dev-shm-usage") # Також корисно для Codespaces/Docker

    # service = Service(executable_path=chromedriver_path)
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    # --- Code for Codespaces GitHub FINISH---

    driver = webdriver.Chrome()  # Переконайтеся, що ChromeDriver знаходиться у вашому PATH
    driver.get(URL)
    print(f"Opened URL is: {URL}")

    close_popup_if_exists(driver, popup_class, close_button_class)

    is_checkbox_present = check_element_presence(driver, checkbox_selector)
    if is_checkbox_present:
        print(f"Checkbox with class name {checkbox_selector} found")
        uncheck_checkbox(driver, checkbox_selector)
    else:
        print(f"Checkbox with class name {checkbox_selector} NOT found")

    is_name_trader_present = check_element_presence(driver, TRADER_CARD_CLASS)
    if is_name_trader_present:
        print(f"{TRADER_CARD_CLASS} found")
        wait_for_element_to_disappear(driver, TRADER_CARD_CLASS)
    else:
        print(f"{TRADER_CARD_CLASS} NOT found")

    is_loading_indicator_present = check_element_presence(driver, loading_indicator_class)
    if is_loading_indicator_present:
        print(f"{loading_indicator_class} found")
        wait_for_element_to_disappear(driver, loading_indicator_class)
    else:
        print(f"{loading_indicator_class} NOT found")    
    
    # trader_data = get_trader_details(driver, TRADER_CARD_CLASS ,SELECTOR_CLASSES)
    # print(trader_data)
    # --- Додаємо виклик для отримання посилань на трейдерів тут ---
    # Отримуємо посилання на трейдерів з карток, припускаючи, що клас карток - "card-outline"
    all_traders_info = get_trader_links(driver, TRADER_CARD_CLASS)
    # print(all_traders_info)

    connection = get_db_connection()

    if connection:        
        # Create all necessary tables
        create_traders_table(connection)
        create_trader_metrics_table(connection)
        create_trader_performance_table(connection)

        print("--- Inserting data for all traders ---")
        for trader_data in all_traders_info:
            trader_id = trader_data.get('trader_id')
            trader_name = trader_data.get('name')
            profile_url = trader_data.get('link')

            # Insert into trader_links_table
            if trader_id and trader_name and profile_url:
                insert_trader_link(connection, trader_id, trader_name, profile_url)
            else:
                print(f"Skipping trader link insertion for incomplete data: {trader_data}")

            # Insert into trader_metrics_table
            # Ensure all expected keys are present, even if 'N/A'
            metrics_to_insert = {
                'trader_id': trader_id,
                'active_followers': trader_data.get('active_followers'),
                'total_spots': trader_data.get('total_spots'),
                'api_availability': trader_data.get('api_availability'),
                'aum_value': trader_data.get('aum_value'),
                'sharpe_ratio_value': trader_data.get('sharpe_ratio_value'),
                'mock_status': trader_data.get('mock_status'),
                'copy_capability': trader_data.get('copy_capability')
            }
            insert_trader_metrics(connection, metrics_to_insert)

            # Insert into trader_performance_metrics
            performance_to_insert = {
                'trader_id': trader_id,
                'period_days': trader_data.get('period_days'),
                'pnl_value_sign': trader_data.get('pnl_value_sign'),
                'pnl_per_period': trader_data.get('pnl_per_period'),
                'roi_value_sign': trader_data.get('roi_value_sign'),
                'roi_per_period': trader_data.get('roi_per_period'),
                'mdd_per_period': trader_data.get('mdd_per_period')
            }
            insert_trader_performance(connection, performance_to_insert)
        
        print("--- Data insertion complete ---")
        db_close_connection(connection)
    else:
        print("Failed to establish database connection. Data insertion aborted.")
        

    
    # for trader_info in all_traders_info:
            
            # add_trader_data(connection, trader_info)
            # print(trader_id)  # Виведе: ID трейдера: 4489719234726598400
            
        # db_close_connection(connection)

    # Отримуємо повний HTML-код сторінки після закриття спливаючого вікна, зняття чекбоксу та очікування
    dom_structure = driver.page_source

    # Зберігаємо DOM-структуру у файл
    try:
        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as file:
            file.write(dom_structure)
        print(f"\nDOM Structure saved to: {OUTPUT_FILENAME}")
    except Exception as e:
        print(f"\nError saving DOM structure to file: {e}")

    # driver.quit()
    pass
print("Скрипт завершено.")
input("Натисніть Enter, щоб закрити...")