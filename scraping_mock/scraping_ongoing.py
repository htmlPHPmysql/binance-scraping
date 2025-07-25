import os # Import module "os"
import sys # New import for system-specific parameters and functions

# Import undetected_chromedriver for enhanced stealth capabilities
import undetected_chromedriver as uc # Import undetected_chromedriver as 'uc'

# Take the absolute path of the base directory
current_script_dir = os.path.dirname(os.path.abspath(__file__))

# Припускаємо, що коренева директорія проекту знаходиться на один рівень вище
# від директорії, де розташований головний скрипт.
# Наприклад, якщо scraping_mock.py знаходиться в C:\Binance_scraping\scraping_mock\,
# тоді project_root_dir буде C:\Binance_scraping\.
root_dir = os.path.dirname(current_script_dir)

# Додаємо кореневу директорію проекту до sys.path.
# Це дозволить Python знаходити модулі, розташовані в підпапках відносно кореня проекту.
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import re
import time
import random # For random delays
import logging # New import for logging
# import psycopg2 # For PostgreSQL
#    
from datetime import datetime
from selenium import webdriver # Keep this import for 'Options' if needed, though uc.ChromeOptions is preferred
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options # Keep this for generic Options, but uc.ChromeOptions is used for uc.Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

from functions.telegram_notifier import send_telegram_message
from functions.logging_setup import (
    setup_logging,
    restore_stdout_stderr
)

from functions.selenium_functions import (
    undetected_chromedriver_add_argument,
    check_presence_element,
    move_cursor,
    click_element,
    add_random_delay,
    human_like_send_keys,
    move_cursor_delay_click
)

from functions.functions_extracting_data import (
    extract_trader_info,
    extract_trader_info_from_ongoing
)

# from functions.functions_google_sheets import (
#     google_sheet_set_connection,
#     google_sheet_open_spreadsheet,
#     google_sheet_open_worksheet,
#     write_to_google_sheet,
#     set_default_cell_color,
#     set_cell_color,
#     get_last_data_row_index
# )

from config import (
        none
    ,   DATA_LOAD_TIMEOUT
    ,   delay_sec_min
    ,   delay_sec_max
)

from config_mock import (
        none
    ,   first_5
    ,   last_5
    ,   spreadsheet_name
    ,   worksheet_name
    ,   URL_LOGIN
    ,   URL_COPY_MANAGEMENT
    ,   COPY_MANAGEMENT_SECTION_DIV_SELECTOR
    ,   SELECTORS
)

from credentials import (
        none # This line seems to be a placeholder, you can remove it if not needed in your actual credential.py
    ,   BINANCE_USERNAME
    ,   BINANCE_PASSWORD
    ,   TELEGRAM_BOT_TOKEN
    ,   TELEGRAM_CHAT_ID
)

if __name__ == "__main__":
    logger = setup_logging(current_script_dir) # Зберігаємо екземпляр логера
    logger.info("Execution of the script is inizialized")

    # --- Code for Codespaces GitHub START (keep commented out as per your request) ---
    # chromedriver_path = "/usr/local/bin/chromedriver" # Шлях до завантаженого вами ChromeDriver

    # chrome_options = Options()
    # chrome_options.add_argument("--headless") # Запускає Chrome без вікна (обов'язково для Codespaces)
    # chrome_options.add_argument("--no-sandbox") # Обов'язково для Codespaces/Docker
    # chrome_options.add_argument("--disable-dev-shm-usage") # Також корисно для Codespaces/Docker

    # service = Service(executable_path=chromedriver_path)
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    # --- Code for Codespaces GitHub FINISH---

    driver = undetected_chromedriver_add_argument(uc, root_dir)
    
    try:
        print(f"Navigating to page: {URL_COPY_MANAGEMENT}")
        
        driver.get(URL_COPY_MANAGEMENT)
        # Get the URL immediately after the initial get() call.
        # This is crucial because JS redirects can happen very quickly.
        page_url_initial = URL_COPY_MANAGEMENT
        # current_page_url = driver.current_url

        redirect_occurred = False
        try:
            print(f"Waiting for URL to change from '{page_url_initial}' (waiting for redirect)...")
            # This will wait until the URL is NOT page_url_initial anymore
            WebDriverWait(driver, DATA_LOAD_TIMEOUT).until(
                EC.url_changes(page_url_initial)
            )
            redirect_occurred = True
            print("URL has changed (redirect detected).")
        except TimeoutException:
            print(f"No redirect detected within {DATA_LOAD_TIMEOUT} seconds. Staying on '{page_url_initial}'.")
            redirect_occurred = False # Explicitly set to false if timeout occurs

        page_url_final = driver.current_url
        print(f"Current final URL after checking for redirect: {page_url_final}")

        if redirect_occurred and URL_LOGIN in page_url_final:

            print("Redirected to login page. Proceeding with login process...")
            
            # Wait for login field to be present (adjust selectors as needed)
            username_field = check_presence_element(
                driver, 
                SELECTORS["input_name"]["selector_type"], 
                SELECTORS["input_name"]["selector_name"], 
                DATA_LOAD_TIMEOUT
            )

            # Inserting username
            human_like_send_keys(username_field, BINANCE_USERNAME)
            # Add random_delay because without this we have message from binance like this:
            # [Cloudflare Turnstile] Invalid input for optional parameter "cData", got "null".
            add_random_delay(delay_sec_min, delay_sec_max)
            move_cursor_delay_click(
                driver,
                SELECTORS["next_button"]["selector_type"],
                SELECTORS["next_button"]["selector_name"]
            )

            # Wait for password field to be present (adjust selectors as needed)
            password_field = check_presence_element(
                driver, 
                SELECTORS["input_pass"]["selector_type"],
                SELECTORS["input_pass"]["selector_name"], 
                DATA_LOAD_TIMEOUT
            )

            # Inserting password
            human_like_send_keys(password_field, BINANCE_PASSWORD)
            add_random_delay(delay_sec_min, delay_sec_max)
            move_cursor_delay_click(
                driver,
                SELECTORS["next_button"]["selector_type"],
                SELECTORS["next_button"]["selector_name"]
            )
            

        elif not redirect_occurred and URL_COPY_MANAGEMENT in page_url_final:
            print("No redirect detected and confirmed on target page. Proceeding with data extraction.")
            print(f"Attempting to find elements with selector: {COPY_MANAGEMENT_SECTION_DIV_SELECTOR}")
            try:
                # Очікуємо, поки будуть присутні ВСІ елементи, що відповідають селектору
                copy_management_sections = WebDriverWait(driver, DATA_LOAD_TIMEOUT).until(
                    # If you want all elements to be visible not only present
                    # EC.visibility_of_all_elements_located((By.CSS_SELECTOR, COPY_MANAGEMENT_SECTION_DIV_SELECTOR))
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, COPY_MANAGEMENT_SECTION_DIV_SELECTOR))
                )
                print(f"Successfully found {len(copy