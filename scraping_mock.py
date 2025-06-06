import re
import psycopg2  # For PostgreSQL
import os # Import module "os"
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_functions import (
    close_popup_if_exists, 
    uncheck_checkbox, 
    check_element_presence, 
    wait_for_element_to_disappear,
    get_trader_links,
    extract_trader_id,
    # get_trader_details
)
from config import (
    URL_COPY_MANAGEMENT,
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
    driver.get(URL_COPY_MANAGEMENT)
    print(f"Opened URL is: {URL_COPY_MANAGEMENT}")

    print("Скрипт завершено.")
    input("Натисніть Enter, щоб закрити...")