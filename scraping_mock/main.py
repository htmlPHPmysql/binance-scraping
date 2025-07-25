

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
    extract_trader_info
)

from functions.functions_google_sheets import (
    google_sheet_set_connection,
    google_sheet_open_spreadsheet,
    google_sheet_open_worksheet,
    write_to_google_sheet,
    set_default_cell_color,
    set_cell_color,
    get_last_data_row_index,
    auto_fit_columns
)

from config import (
    DATA_LOAD_TIMEOUT,
    OUTPUT_FILENAME,
    delay_sec_min,
    delay_sec_max,
    checkbox_selector,
    pages_selector,
    name_trader_class,
    loading_indicator_class,
    TRADER_CARD_CLASS,
    SELECTOR_CLASSES
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
        logger.info(f"Navigating to page: {URL_COPY_MANAGEMENT}")
        # driver.get(URL_LOGIN)
        driver.get(URL_COPY_MANAGEMENT)
        # Get the URL immediately after the initial get() call.
        # This is crucial because JS redirects can happen very quickly.
        initial_page_url = URL_COPY_MANAGEMENT
        current_page_url = driver.current_url
        # print(f"Initial URL after requesting target: {initial_page_url}")

        redirect_occurred = False
        try:
            print(f"Waiting for URL to change from '{initial_page_url}' (waiting for redirect)...")
            # This will wait until the URL is NOT initial_page_url anymore
            WebDriverWait(driver, DATA_LOAD_TIMEOUT).until(
                EC.url_changes(initial_page_url)
            )
            redirect_occurred = True
            print("URL has changed (redirect detected).")
        except TimeoutException:
            print(f"No redirect detected within {DATA_LOAD_TIMEOUT} seconds. Staying on '{initial_page_url}'.")
            redirect_occurred = False # Explicitly set to false if timeout occurs

        current_final_url = driver.current_url
        print(f"Current final URL after checking for redirect: {current_final_url}")

        if redirect_occurred and URL_LOGIN in current_final_url:

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
            
            if password_field:
                # Inserting password
                human_like_send_keys(password_field, BINANCE_PASSWORD)
                add_random_delay(delay_sec_min, delay_sec_max)
                move_cursor_delay_click(
                    driver,
                    SELECTORS["next_button"]["selector_type"],
                    SELECTORS["next_button"]["selector_name"]
                )
            else:
                logger.error(f"password_field variable is None")
                modal_window = check_presence_element(
                    driver, 
                    SELECTORS["modal_confirm"]["selector_type"], 
                    SELECTORS["modal_confirm"]["selector_name"], 
                    "1"
                )
                if modal_window:
                    modal_window_text = modal_window.text
                    logger.info(f"text: {modal_window_text}")
                    add_random_delay(delay_sec_min, delay_sec_max)

            # Checking of the presence Security Verification "Open Binance app on your phone"
            security_verification = check_presence_element(
                driver, 
                SELECTORS["security_verification"]["selector_type"],
                SELECTORS["security_verification"]["selector_name"], 
                DATA_LOAD_TIMEOUT
            )
            if security_verification:
                security_verification_text = security_verification.text
                logger.info(f"text: {security_verification_text}")
            else:
                logger.error(f"security_verification variable is None")
                modal_window = check_presence_element(
                    driver, 
                    SELECTORS["modal_confirm"]["selector_type"], 
                    SELECTORS["modal_confirm"]["selector_name"], 
                    "1"
                )
                if modal_window:
                    modal_window_text = modal_window.text
                    logger.info(f"text: {modal_window_text}")
                    add_random_delay(delay_sec_min, delay_sec_max)
            

        elif not redirect_occurred and URL_COPY_MANAGEMENT in current_final_url:
            print("No redirect detected and confirmed on target page. Proceeding with data extraction.")

            print("Attempting to click the 'Mock Copy Trading' tab (id='bn-tab-Copy')...")
            move_cursor_delay_click(
                driver,
                SELECTORS["tab_mock"]["selector_type"],
                SELECTORS["tab_mock"]["selector_name"]
            )

            print(f"Attempting to find elements with selector: {COPY_MANAGEMENT_SECTION_DIV_SELECTOR}")
            try:
                # Очікуємо, поки будуть присутні ВСІ елементи, що відповідають селектору
                copy_management_sections = WebDriverWait(driver, DATA_LOAD_TIMEOUT).until(
                    # If you want all elements to be visible not only present
                    # EC.visibility_of_all_elements_located((By.CSS_SELECTOR, COPY_MANAGEMENT_SECTION_DIV_SELECTOR))
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, COPY_MANAGEMENT_SECTION_DIV_SELECTOR))
                )
                print(f"Successfully found {len(copy_management_sections)} copy management section div(s).")
                
                google_connection = google_sheet_set_connection()
                
                spreadsheet = google_sheet_open_spreadsheet(google_connection, spreadsheet_name)
                
                worksheet = google_sheet_open_worksheet(spreadsheet, worksheet_name)
                # Тепер 'copy_management_sections' є списком WebElement-ів,
                # з якими ви можете працювати далі.
                # Наприклад, вивести їхній текст або знайти в них інші елементи.
                sum_roi = 0.0  # Initialize sum_roi
                params_search = first_5
                for i, section_div in enumerate(copy_management_sections):

                    # print(f"DEBUG: Type of section_div: {type(section_div)}") 
                    # print(f"DEBUG: Content of section_div: {section_div}") # This will print the raw WebElement object, useful if not a tuple
                    mock_trader_text = section_div.text
                    trader_name, roi_value = extract_trader_info(mock_trader_text, logger)
                    # sum_roi += (roi_value if roi_value is not None else 0.0) # Add ROI to sum_roi
                    sum_roi += roi_value # Add ROI to sum_roi

                    current_time = datetime.now()
                    
                    # Insert data into Google Sheet
                    trader_data = {
                        "Timestamp":    current_time,
                        "SearchParams": params_search,
                        "TraderName":   trader_name,
                        "ROIValue":     roi_value,
                        "ROIsum":       sum_roi
                    }
                    write_to_google_sheet(trader_data, worksheet)
                    current_row_index = get_last_data_row_index(worksheet)
                    set_default_cell_color(worksheet, current_row_index) # Can reach API limits                   
                                        
                    if i == 4:
                        params_search = last_5

                        if sum_roi > 0:
                            set_cell_color(worksheet, current_row_index, "E", "#90EE90")
                        elif sum_roi < 0:
                            set_cell_color(worksheet, current_row_index, "E", "#FF6666")  

                        message = f"Total sum_roi {sum_roi}"
                        send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message)

                        sum_roi = 0.0
                
                if sum_roi > 0:
                    set_cell_color(worksheet, current_row_index, "E", "#90EE90")
                elif sum_roi < 0:
                    set_cell_color(worksheet, current_row_index, "E", "#FF6666")

                message = f"Total sum_roi {sum_roi}"
                send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message)

                auto_fit_columns(worksheet, 1, 5, logger)

            except TimeoutException:
                print(f"Timeout: No elements with selector '{COPY_MANAGEMENT_SECTION_DIV_SELECTOR}' found within {DATA_LOAD_TIMEOUT} seconds.")
                raise Exception("Could not find expected copy management section divs.")
            except Exception as e:
                print(f"An unexpected error occurred while finding divs: {e}")
                raise

        else:
            print(f"Unexpected page state. Redirect occurred but not to login, or neither expected page. Current URL: {current_final_url}")
            raise Exception(f"Unexpected URL or redirect: {current_final_url}")

        
        
        # driver.find_element(By.ID, "password").send_keys(BINANCE_PASSWORD) # This line is commented out and thus not executed
    except Exception as e:
        print(f"An error occurred in the main script: {e}")
    finally:
        print("Script is completed")
        input("Натисніть Enter, щоб закрити...")
        if driver:
            driver.quit()            
            print("Browser is closed")
        restore_stdout_stderr() # Відновлюємо стандартні потоки виводу
        
       