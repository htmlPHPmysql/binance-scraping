

import re
# import psycopg2 # For PostgreSQL
import os # Import module "os"
import time
import random # For random delays
import logging # New import for logging
import sys # New import for system-specific parameters and functions

# Import undetected_chromedriver for enhanced stealth capabilities
import undetected_chromedriver as uc # Import undetected_chromedriver as 'uc'

from datetime import datetime
from selenium import webdriver # Keep this import for 'Options' if needed, though uc.ChromeOptions is preferred
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options # Keep this for generic Options, but uc.ChromeOptions is used for uc.Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException


from selenium_functions import (
    undetected_chromedriver_add_argument,
    check_presence_element,
    move_cursor,
    click_element,
    add_random_delay,
    human_like_send_keys
)

from functions_extracting_data import (
    extract_trader_info
)

from functions_google_sheets import (
    google_sheet_set_connection,
    google_sheet_open_spreadsheet,
    google_sheet_open_worksheet,
    write_to_google_sheet
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
    SELECTOR_CLASSES,
    COPY_MANAGEMENT_SECTION_DIV_SELECTOR
)
from credential import (
        none # This line seems to be a placeholder, you can remove it if not needed in your actual credential.py
    ,   URL_LOGIN
    ,   URL_COPY_MANAGEMENT
    ,   BINANCE_USERNAME
    ,   BINANCE_PASSWORD
)


# --- Logging Setup ---
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOG_DIR, exist_ok=True) # Ensure the logs directory exists

LOG_FILE_PATH = os.path.join(LOG_DIR, 'mock_scraper.log')

# Configure logging to output to a file and console
logging.basicConfig(
    level=logging.INFO, # Set the base logging level. Messages of INFO, WARNING, ERROR, CRITICAL will be processed.
    format='%(asctime)s - %(levelname)s - %(message)s', # Format of log messages
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, encoding='utf-8'), # Log to a file
        logging.StreamHandler() # Log to the console
    ]
)
logger = logging.getLogger(__name__) # Get a logger instance for this module

# --- Redirect print() output to logger ---
class LoggerWriter:
    """
    Custom file-like object to redirect sys.stdout and sys.stderr to the logger.
    """
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.buffer = ''

    def write(self, message):
        # Buffer messages until a newline is encountered
        self.buffer += message
        if '\n' in self.buffer:
            lines = self.buffer.split('\n')
            for line in lines[:-1]:
                if line: # Avoid logging empty strings
                    self.logger.log(self.level, line.rstrip()) # Log the line, removing trailing newline
            self.buffer = lines[-1] # Keep the last (incomplete) line in buffer

    def flush(self):
        # Log any remaining content in the buffer when flush is called
        if self.buffer:
            self.logger.log(self.level, self.buffer.rstrip())
            self.buffer = ''

# Redirect stdout and stderr to the logger
sys.stdout = LoggerWriter(logger, logging.INFO)
sys.stderr = LoggerWriter(logger, logging.ERROR)
# Note: After this redirection, all subsequent print() calls will go to the logger.
# This means your existing print() statements will now be logged.

if __name__ == "__main__":
    # --- Code for Codespaces GitHub START (keep commented out as per your request) ---
    # chromedriver_path = "/usr/local/bin/chromedriver" # Шлях до завантаженого вами ChromeDriver

    # chrome_options = Options()
    # chrome_options.add_argument("--headless") # Запускає Chrome без вікна (обов'язково для Codespaces)
    # chrome_options.add_argument("--no-sandbox") # Обов'язково для Codespaces/Docker
    # chrome_options.add_argument("--disable-dev-shm-usage") # Також корисно для Codespaces/Docker

    # service = Service(executable_path=chromedriver_path)
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    # --- Code for Codespaces GitHub FINISH---

    driver = undetected_chromedriver_add_argument(uc)
    
    try:
        print(f"Navigating to page: {URL_COPY_MANAGEMENT}")
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
            username_field = check_presence_element(driver, By.NAME, "username", DATA_LOAD_TIMEOUT)

            # Inserting username
            human_like_send_keys(username_field, BINANCE_USERNAME)
            # Add random_delay because without this we have message from binance like this:
            # [Cloudflare Turnstile] Invalid input for optional parameter "cData", got "null".
            add_random_delay(delay_sec_min, delay_sec_max)

            # Move the cursor over the element
            move_cursor(driver, By.CLASS_NAME, 'bn-button__primary', DATA_LOAD_TIMEOUT)
            add_random_delay(delay_sec_min, delay_sec_max)

            # Click the button
            click_element(driver, By.CLASS_NAME, 'bn-button__primary', DATA_LOAD_TIMEOUT)

            # Wait for password field to be present (adjust selectors as needed)
            password_field = check_presence_element(driver, By.ID, "password-input", DATA_LOAD_TIMEOUT)

            # Inserting password
            human_like_send_keys(password_field, BINANCE_PASSWORD)
            add_random_delay(delay_sec_min, delay_sec_max)

            # Move the cursor over the element
            move_cursor(driver, By.CLASS_NAME, 'bn-button__primary', DATA_LOAD_TIMEOUT)
            add_random_delay(delay_sec_min, delay_sec_max)

            # Click the login button or any "Next" button using its aria-label
            click_element(driver, By.CLASS_NAME, 'bn-button__primary', DATA_LOAD_TIMEOUT)

        elif not redirect_occurred and URL_COPY_MANAGEMENT in current_final_url:
            print("No redirect detected and confirmed on target page. Proceeding with data extraction.")

            print("Attempting to click the 'Mock Copy Trading' tab (id='bn-tab-Copy')...")
            move_cursor(driver, By.ID, 'bn-tab-Copy', DATA_LOAD_TIMEOUT)
            add_random_delay(delay_sec_min, delay_sec_max)
            click_element(driver, By.ID, "bn-tab-Copy", DATA_LOAD_TIMEOUT)

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

                spreadsheet_name = "Binance mock"
                spreadsheet = google_sheet_open_spreadsheet(google_connection, spreadsheet_name)

                worksheet_name = "2"
                worksheet = google_sheet_open_worksheet(spreadsheet, worksheet_name)
                # Тепер 'copy_management_sections' є списком WebElement-ів,
                # з якими ви можете працювати далі.
                # Наприклад, вивести їхній текст або знайти в них інші елементи.
                sum_roi = 0.0  # Initialize sum_roi
                for i, section_div in enumerate(copy_management_sections):

                    # print(f"DEBUG: Type of section_div: {type(section_div)}") 
                    # print(f"DEBUG: Content of section_div: {section_div}") # This will print the raw WebElement object, useful if not a tuple
                    mock_trader_text = section_div.text
                    trader_name, roi_value = extract_trader_info(mock_trader_text)
                    # sum_roi += (roi_value if roi_value is not None else 0.0) # Add ROI to sum_roi
                    sum_roi += roi_value # Add ROI to sum_roi

                    current_time = datetime.now()
        
                    # Insert data into Google Sheet
                    write_to_google_sheet(current_time, trader_name, roi_value, sum_roi, worksheet)
                

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
        print(f"An error occurred: {e}")
    finally:
        print("Скрипт завершено.")
        input("Натисніть Enter, щоб закрити...")
        # driver.quit() # This line was commented out in your original code, meaning the browser might not close automatically