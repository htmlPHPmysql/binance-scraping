import re
import psycopg2  # Для PostgreSQL
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, 
    TimeoutException, 
    StaleElementReferenceException
)
from selenium_functions import (
    close_popup_if_exists, 
    uncheck_checkbox, 
    check_element_presence, 
    wait_for_element_to_disappear,
    get_trader_links,
    extract_trader_id
)  # Імпортуємо функції
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
    trader_card_class
)
from sql_functions import (
    add_trader_data,
    get_db_connection,
    db_close_connection
)

if __name__ == "__main__":
    driver = webdriver.Chrome()  # Переконайтеся, що ChromeDriver знаходиться у вашому PATH
    driver.get(URL)
    print(f"Відкрито URL: {URL}")

    close_popup_if_exists(driver, popup_class, close_button_class)

    is_checkbox_present = check_element_presence(driver, checkbox_selector)
    if is_checkbox_present:
        print(f"{checkbox_selector} found")
        uncheck_checkbox(driver, (By.CLASS_NAME, checkbox_selector))
    else:
        print(f"{checkbox_selector} NOT found")

    is_name_trader_present = check_element_presence(driver, name_trader_class)
    if is_name_trader_present:
        print(f"{name_trader_class} found")
        wait_for_element_to_disappear(driver, name_trader_class)
    else:
        print(f"{name_trader_class} NOT found")

    is_loading_indicator_present = check_element_presence(driver, loading_indicator_class)
    if is_loading_indicator_present:
        print(f"{loading_indicator_class} found")
        wait_for_element_to_disappear(driver, loading_indicator_class)
    else:
        print(f"{loading_indicator_class} NOT found")    
    
    # --- Додаємо виклик для отримання посилань на трейдерів тут ---
    # Отримуємо посилання на трейдерів з карток, припускаючи, що клас карток - "card-outline"
    trader_links_list = get_trader_links(driver, trader_card_class)
    if trader_links_list:

        connection = get_db_connection()
        for link in trader_links_list:
            trader_id = extract_trader_id(link)
            if trader_id:
                add_trader_data(connection, trader_id, link)
                # print(trader_id)  # Виведе: ID трейдера: 4489719234726598400
            else:
                print(f"ID трейдера не знайдено у {link}.")
        db_close_connection(connection)

    else:

        print("\nНе вдалося отримати посилання на профілі трейдерів.")
    # --- Кінець блоку отримання посилань на трейдерів ---

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