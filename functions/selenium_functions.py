# selenium_functions.py
# from selenium_functions import close_popup_if_exists, uncheck_checkbox  # Імпортуємо функції
import re
import os
import time
import random # For random delays
import logging
# import psycopg2  # Для PostgreSQL
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

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

from scraping_mock.config_mock import (
        none
    ,   first_5
    ,   last_5
    ,   spreadsheet_name
    ,   worksheet_name    
    ,   COPY_MANAGEMENT_SECTION_DIV_SELECTOR
    ,   SELECTORS
)

# Отримуємо логер, який вже налаштований у головному скрипті
logger = logging.getLogger(__name__)

def close_popup_if_exists(driver, popup_class_name, close_button_class_name):
    try:
        popup = WebDriverWait(driver, DATA_LOAD_TIMEOUT).until(
            EC.presence_of_element_located((By.CLASS_NAME, popup_class_name))
        )
        print("Popup window found.")
        close_button = WebDriverWait(driver, DATA_LOAD_TIMEOUT).until(
            EC.element_to_be_clickable((By.CLASS_NAME, close_button_class_name))
        )
        close_button.click()
        print("Popup window closed.")
        return True
    except TimeoutException:
        print("Popup window not found within the timeout, proceeding without closing.")
        return False
    except NoSuchElementException:
        print("Close button not found within the popup.")
        return False

def uncheck_checkbox(driver, checkbox_selector):
    try:
        checkbox = WebDriverWait(driver, DATA_LOAD_TIMEOUT).until(
            EC.presence_of_element_located((By.CLASS_NAME, checkbox_selector))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
        
        try:
            WebDriverWait(driver, DATA_LOAD_TIMEOUT).until(
                EC.element_to_be_clickable((By.CLASS_NAME, checkbox_selector))
            )
            print(f"Checkbox {checkbox_selector} is clickable")
            aria_checked = checkbox.get_attribute("aria-checked")
            if aria_checked == "true":
                checkbox.click()
                print(f"Checkbox with class name {checkbox_selector} unchecked (after scrolling into view)")
                return True
            else:
                print(f"Checkbox with class name {checkbox_selector} is already unchecked")
                return True
        except TimeoutException:
            print(f"Timeout: Checkbox with class name {checkbox_selector} isn't clickable during {DATA_LOAD_TIMEOUT} secs")
            # Тут ви можете додати логіку для обробки ситуації, коли елемент не з'явився,
            # наприклад, зробити скріншот, записати в лог, або повторити спробу.
        except Exception as e:
            print(f"Other unexpected error occure: {e}")

    except TimeoutException:
        print("Checkbox not found or not clickable within the timeout.")
        return False
    except NoSuchElementException:
        print("Checkbox element not found.")
        return False
    except StaleElementReferenceException as e:
        print(f"Checkbox element is stale! {e}")
        return False
    
def check_element_presence(driver, selector):
    """
    Негайно перевіряє наявність елемента на сторінці без явного очікування.
    
    :param driver: Екземпляр WebDriver.
    :param selector: Кортеж (By.ТИП_ЛОКАТОРА, "значення_локатора"), наприклад, (By.CLASS_NAME, "my-element").
    :return: True, якщо елемент знайдено, False в іншому випадку.
    """
    elements = driver.find_elements(By.CLASS_NAME, selector) # *selector розпаковує кортеж
    return len(elements) > 0 # Повертає True, якщо знайдено хоча б один елемент

def wait_for_element_to_disappear(driver, locator):
    """
    Чекає, поки елементи зникнуть.

    :param driver: Екземпляр WebDriver.
    :param locator: Клас CSS, який позначає елемент дом дерева.
    :param DATA_LOAD_TIMEOUT: Максимальний час очікування (в секундах).
    :return: True, якщо елементи зникли, False, якщо стався таймаут.
    """
    try:
        print(f"Очікування зникнення елементу ('{locator}') протягом {DATA_LOAD_TIMEOUT} секунд...")
        WebDriverWait(driver, DATA_LOAD_TIMEOUT).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, locator))
        )
        print(f"Елементи ('{locator}') зникли. Нові дані завантажено.")
        return True
    except TimeoutException:
        print(f"Таймаут очікування зникнення елементів ('{locator}').")
        return False
    except StaleElementReferenceException:
        # Цей виняток може виникнути, якщо елемент зникає під час спроби Selenium взаємодіяти з ним.
        # У контексті EC.invisibility_of_element_located, це зазвичай означає, що він зник успішно.
        print(f"Елементи ('{locator}') зникли під час перевірки (StaleElementReferenceException).")
        return True

def check_presence_element(driver, by_type, selector, timeout):
    """
    Waits for an element to be visible

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        by_type (By): The By strategy (e.g., By.NAME, By.ID, By.CSS_SELECTOR).
        selector (str): The selector string for the element.
        timeout (int): The maximum time to wait for the element in seconds.        
        
    Returns:
        WebElement: The found WebElement if successful, None otherwise.
    """
    try:

        print(f"({by_type}='{selector}') waiting for element to be present")
        
        element = WebDriverWait(driver, timeout).until(
            # Чекає, поки елемент присутній у DOM (Елемент може бути присутнім, але невидимим або знаходитися за межами області перегляду)
            # EC.presence_of_element_located((by_type, selector))

            # Чекає, поки елемент присутній у DOM І є видимим (означає, що елемент має ширину та висоту, більші за 0, і не має стилів display: none; або visibility: hidden;)
            EC.visibility_of_element_located((by_type, selector))
        )
                    
        print(f"({by_type}='{selector}') is visible")

        return element

    except TimeoutException:
        print(f"Error: ({by_type}='{selector}') not found within {timeout} seconds.")
        return None
    
    except NoSuchElementException:
        print(f"Error: Element not found by selector '{selector}'.")
        return None
    
    except Exception as e:
        print(f"An unexpected error occurred while interacting with ({by_type}='{selector}'): {e}")
        return None
    
def move_cursor(driver, by_type, selector, timeout):
    """
    Waits for an element to be clickable  and move the cursor over the elemnt (button).

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        by_type (By): The By strategy (e.g., By.NAME, By.ID, By.CSS_SELECTOR).
        selector (str): The selector string for the element.
        timeout (int): The maximum time to wait for the element in seconds.        

    Returns:
        None
    """
    try:
        print(f"({by_type}='{selector}') checking to be clickable")
        
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by_type, selector))
        )
        
        print(f"({by_type}='{selector}') is clickable")
        
        actions = ActionChains(driver)        
        actions.move_to_element(element).perform()
        print(f"Action 'move_to_element' performed. ({by_type}='{selector}') has the cursor hovered")       

    except TimeoutException:
        print(f"Error: ({by_type}='{selector}') is not interactable within {timeout} seconds.")
        return None
    except NoSuchElementException:
        print(f"Error: ({by_type}='{selector}') not found by selector '{selector}'.")
        return None
    except Exception as e:
        print(f"Could not click the button ({by_type}='{selector}'): {e}")
        return None
    
def click_element(driver, by_type, selector, timeout):
    """
    Waits for an element to be clickable and optionally performs an action (click).

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        by_type (By): The By strategy (e.g., By.NAME, By.ID, By.CSS_SELECTOR).
        selector (str): The selector string for the element.
        timeout (int): The maximum time to wait for the element in seconds.        

    Returns:
        None
    """
    try:
        print(f"({by_type}='{selector}') checking to be clickable")
        
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by_type, selector))
        )
        if element:
            print(f"({by_type}='{selector}') is clickable")
        
        actions = ActionChains(driver)        
        actions.click().perform()
        print(f"Action 'click' performed. ({by_type}='{selector}') clicked button")       

    except TimeoutException:
        # print(f"Error: ({by_type}='{selector}') is not interactable within {timeout} seconds.")
        logger.error(f"Error: ({by_type}='{selector}') is not interactable within {timeout} seconds.")
        return None
    except NoSuchElementException:
        print(f"Error: ({by_type}='{selector}') not found by selector '{selector}'.")
        return None
    except Exception as e:
        print(f"Could not click the button ({by_type}='{selector}'): {e}")
        return None

def add_random_delay(min_seconds, max_seconds):
    """
    Introduces a random programmatic delay between min_seconds and max_seconds.

    Args:
        min_seconds (float): The minimum number of seconds for the delay.
        max_seconds (float): The maximum number of seconds for the delay.
    """
    random_delay = random.uniform(min_seconds, max_seconds)
    print(f"Adding a programmatic delay of {random_delay:.2f} seconds...")
    time.sleep(random_delay)

def human_like_send_keys(element, text):
    if text is None:
        error_message = f"Attempt to enter None value. Text: {text}"
        raise Exception(error_message) 
    
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2)) # Delay between 50ms and 200ms per character
    print(f"({element}') entered value")

def move_cursor_delay_click(driver, selector_type, selector_name):
    """
    Execute 3 moves:
    1) move to the cursor
    2) add random delay
    3) click defined element
    
    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        selector_type (By): The By strategy (e.g., By.NAME, By.ID, By.CSS_SELECTOR).
        selector_name (str): The selector string for the element.
    Returns:
        None
    """
    # Move the cursor over the element
    move_cursor(
        driver,
        selector_type,
        selector_name, 
        DATA_LOAD_TIMEOUT
    )
    add_random_delay(delay_sec_min, delay_sec_max)

    # Click the login button or any "Next" button using its aria-label
    click_element(
        driver,
        selector_type,
        selector_name,  
        DATA_LOAD_TIMEOUT
    )

# def perform_login_sequence(driver):
#     """
#     Виконує повну послідовність входу в систему Binance.
#     Очікується, що драйвер знаходиться на сторінці входу Binance.
#     """
#     # Wait for login field to be present (adjust selectors as needed)
#     username_field = check_presence_element(
#         driver, 
#         SELECTORS["input_name"]["selector_type"], 
#         SELECTORS["input_name"]["selector_name"], 
#         DATA_LOAD_TIMEOUT
#     )

#     # Inserting username
#     human_like_send_keys(username_field, BINANCE_USERNAME)
#     # Add random_delay because without this we have message from binance like this:
#     # [Cloudflare Turnstile] Invalid input for optional parameter "cData", got "null".
#     add_random_delay(delay_sec_min, delay_sec_max)

#     # Move the cursor over the element
#     move_cursor(
#         driver, 
#         SELECTORS["next_button"]["selector_type"],
#         SELECTORS["next_button"]["selector_name"], 
#         DATA_LOAD_TIMEOUT
#     )
#     add_random_delay(delay_sec_min, delay_sec_max)

#     # Click the button
#     click_element(
#         driver,
#         SELECTORS["next_button"]["selector_type"],
#         SELECTORS["next_button"]["selector_name"], 
#         DATA_LOAD_TIMEOUT
#     )

#     # Wait for password field to be present (adjust selectors as needed)
#     password_field = check_presence_element(
#         driver, 
#         SELECTORS["input_pass"]["selector_type"],
#         SELECTORS["input_pass"]["selector_name"], 
#         DATA_LOAD_TIMEOUT
#     )

#     # Inserting password
#     human_like_send_keys(password_field, BINANCE_PASSWORD)
#     add_random_delay(delay_sec_min, delay_sec_max)

#     # Move the cursor over the element
#     move_cursor(
#         driver,
#         SELECTORS["next_button"]["selector_type"],
#         SELECTORS["next_button"]["selector_name"], 
#         DATA_LOAD_TIMEOUT
#     )
#     add_random_delay(delay_sec_min, delay_sec_max)

#     # Click the login button or any "Next" button using its aria-label
#     click_element(
#         driver,
#         SELECTORS["next_button"]["selector_type"],
#         SELECTORS["next_button"]["selector_name"],  
#         DATA_LOAD_TIMEOUT
#     )

def undetected_chromedriver_add_argument(uc, aim_dir):

    # Configure options for undetected_chromedriver
    # uc.ChromeOptions is used instead of selenium.webdriver.ChromeOptions for better compatibility
    chrome_options = uc.ChromeOptions()
    # You can add arguments here if needed, for example, for headless mode:
    chrome_options.add_argument("--headless") # Uncomment if you want to run without a visible browser UI
    
    chrome_options.add_argument("--no-sandbox")

    chrome_options.add_argument("--disable-dev-shm-usage")

    # For Ukrainian, then English US, then general English
    chrome_options.add_argument("--lang=uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7")

    chrome_options.add_argument("--start-maximized") # Maximizes the browser window
    # OR
    # chrome_options.add_argument("--window-size=1920,1080") # Specific common resolution

    # This is a very important one. Selenium (and other automation tools) set a JavaScript flag 
    # (navigator.webdriver) that websites can detect. undetected_chromedriver aims to handle this, 
    # but explicitly adding this argument can be an extra layer of defense.
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # Add a user agent to mimic a real browser (optional, but good practice)
    # BY THE WAY this is helpfull for eliminate slider CAPTCHAs
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")

    # While Flash is mostly dead, some older anti-bot systems might check for Flash-related permissions.
    chrome_options.add_argument("--disable-features=EnableEphemeralFlashPermission")

    # Sometimes disabling certain experimental features can make the browser behave
    # more like a standard, older version
    chrome_options.add_argument("--disable-site-isolation-trials")

    # incognito mode can sometimes help, as it ensures a clean session without 
    # pre-existing cookies or cache, reducing the "history" footprint
    # chrome_options.add_argument("--incognito")

    # Create 'chrome_profile' folder in the root folder
    # del_when_session_not_created_cannot_connect_to_chrome
    # json.decoder.JSONDecodeError: Unterminated string starting at: line 1 column 8180 (char 8179)
    profile_dir = os.path.join(aim_dir, "chrome_profile_del_when_session_not_created_cannot_connect_to_chrome")
    
    # Створіть директорію для профілю, якщо вона не існує
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)
        print(f"Created Chrome profile directory: {profile_dir}")
    
    chrome_options.add_argument(f"--user-data-dir={profile_dir}")

    # Disable Password Manager and Credentials Service: Sometimes these can trigger internal browser behaviors
    # that are not typical for a fresh, non-human-controlled session.
    chrome_options.add_experimental_option(
        "prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False}
    )

    # Initialize the WebDriver using undetected_chromedriver
    # This automatically handles ChromeDriver executable download and patching for stealth.
    driver = uc.Chrome(options=chrome_options) # Replaced webdriver.Chrome() with uc.Chrome()
    # If you were using a specific chromedriver_path, you would remove it.
    # For Codespaces, if you uncommented the Codespaces section, you might need to adjust.
    # For local Windows/macOS, just `uc.Chrome()` is usually enough.

    return driver

