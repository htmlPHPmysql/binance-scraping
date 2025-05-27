# selenium_functions.py
# from selenium_functions import close_popup_if_exists, uncheck_checkbox  # Імпортуємо функції
import re
import psycopg2  # Для PostgreSQL
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from config import (
    URL,
    DATA_LOAD_TIMEOUT,
    OUTPUT_FILENAME,
    popup_class,
    close_button_class,
    checkbox_selector,
    pages_selector,
    name_trader_class,
    loading_indicator_class
)

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
    
def get_trader_links(driver, trader_card_class):
    """
    Отримує посилання на профілі трейдерів з карток.

    :param driver: Екземпляр WebDriver.
    :param trader_card_class: Клас елементів, які містять картки з інформацією про трейдерів.
    :return: Список посилань на профілі трейдерів.  Повертає порожній список, якщо елементи не знайдені.
    """
    all_traders_info = []
    try:
        # Знаходимо всі елементи div з заданим класом картки
        card_elements = driver.find_elements(By.CLASS_NAME, trader_card_class)
        for card in card_elements:
            try:
                # В кожній картці знаходимо посилання на профіль трейдера.  Припускаємо, що посилання знаходиться в тегу <a>.
                # Це може бути змінено, якщо структура вашого HTML відрізняється.
                a_tag = card.find_element(By.TAG_NAME, "a")
                link = a_tag.get_attribute("href")
                trader_id = extract_trader_id(link)
                link_text = a_tag.text.strip()
                trader_metrics = parse_trader_full_metrics(link_text)
                trader_info = {"trader_id": trader_id}
                
                trader_info.update(trader_metrics)
                link = {"link": link}
                trader_info.update(link)
                all_traders_info.append(trader_info)
                # all_traders_info.update(trader_metrics)
            except NoSuchElementException:
                print("Посилання на трейдера не знайдено в одній з карток.")
                # Якщо посилання не знайдено в картці, продовжуємо обробку інших карток
                continue
        print(f"{len(all_traders_info)} lead traders links are found")
    except NoSuchElementException:
        print(f"Елементи з класом '{trader_card_class}' не знайдено.")
    return all_traders_info

def extract_trader_id(url):
    """
    Витягає ID трейдера з URL.

    :param url: URL профілю трейдера Binance Copy Trading.
    :return: ID трейдера у вигляді рядка, або None, якщо ID не знайдено.
    """
    match = re.search(r"/lead-details/(\d+)", url)
    if match:
        return match.group(1)
    else:
        return None
    
def parse_trader_full_metrics(data_string: str) -> dict:
    """
    Parses a multi-line string containing various trader metrics and returns a dictionary
    with extracted data. This function is designed to be more robust to missing
    optional fields by searching for keywords.

    Args:
        data_string: The input string containing trader metrics, separated by newlines.

    Returns:
        A dictionary with parsed trader data. Returns an empty dictionary if parsing fails
        due to unexpected format.
    """
    # Split the input string into lines and strip whitespace, filtering out empty lines.
    lines = [line.strip() for line in data_string.strip().split('\n') if line.strip()]

    # Initialize the dictionary with default 'N/A' values for all expected fields.
    # This ensures all keys are present in the output, even if data is missing.
    trader_metrics = {
        'name': 'N/A',
        'active_followers': 'N/A',
        'total_spots': 'N/A',
        'api_availability': 'N/A', # This field will be updated if "API" is found in the input string.
        'period_days': 'N/A', # Consolidated field for period (e.g., 30 from "30 Days PNL")
        'pnl_value_sign': 'N/A', # Field for the sign of PnL value
        'pnl_per_period': 'N/A', # Renamed from pnl_value
        'roi_value_sign': 'N/A', # Field for the sign of ROI value (moved up)
        'roi_per_period': 'N/A', # Renamed from roi_value (moved down)
        'aum_value': 'N/A',
        'mdd_per_period': 'N/A', # Corrected typo from mdd_value_preiod
        'sharpe_ratio_value': 'N/A',
        'mock_status': 'N/A',
        'copy_capability': 'N/A'
    }

    # If no lines are parsed, return an empty dictionary.
    if not lines:
        print("Error: Input data string is empty or contains no meaningful lines.")
        return {}

    # The first line is always the trader's name.
    trader_metrics['name'] = lines[0]

    # The second line typically contains active followers and total spots, e.g., "36 / 600".
    if len(lines) > 1:
        followers_spots_parts = lines[1].split(' / ')
        if len(followers_spots_parts) == 2:
            trader_metrics['active_followers'] = followers_spots_parts[0]
            trader_metrics['total_spots'] = followers_spots_parts[1]
        else:
            print(f"Warning: Could not parse active_followers/total_spots from '{lines[1]}'")

    # Iterate through the rest of the lines (starting from the third line, index 2)
    # to find specific metrics based on keywords. This makes parsing more resilient
    # to variations in the presence or order of optional fields.
    i = 2 
    while i < len(lines):
        line = lines[i]

        # Check for the "API" keyword. If found, assign the entire line to 'api_availability'.
        if "API" in line:
            trader_metrics['api_availability'] = line
        # Check for "PNL" keyword. If found, assign the line as period and the next line as value.
        elif "PNL" in line:
            # Extract only the numerical part for 'period_days'
            match = re.search(r'(\d+)', line)
            if match and trader_metrics['period_days'] == 'N/A': # Set period_days only if not already set
                trader_metrics['period_days'] = match.group(1)

            if i + 1 < len(lines): # Ensure there's a next line for the value
                raw_pnl_value = lines[i+1]
                # Extract the sign and the number part for pnl_value
                pnl_match = re.match(r'([+-])?(.+)', raw_pnl_value)
                if pnl_match:
                    # Assign sign first, then value
                    trader_metrics['pnl_value_sign'] = pnl_match.group(1) if pnl_match.group(1) else '' # Store '+' or '-' or empty string
                    # Clean the number part: remove commas and percentage signs
                    trader_metrics['pnl_per_period'] = pnl_match.group(2).replace(',', '').replace('%', '')
                else:
                    trader_metrics['pnl_value_sign'] = 'N/A' # Default sign if no match
                    trader_metrics['pnl_per_period'] = raw_pnl_value.replace(',', '').replace('%', '') # Store as is if no match, but clean
                i += 1 # Advance index to skip the value line as it's already processed
        # Check for "ROI" keyword.
        elif "ROI" in line:
            if i + 1 < len(lines):
                raw_roi_value = lines[i+1]
                # Extract the sign and the number part for roi_value
                roi_match = re.match(r'([+-])?(.+)', raw_roi_value)
                if roi_match:
                    # Assign sign first, then value
                    trader_metrics['roi_value_sign'] = roi_match.group(1) if roi_match.group(1) else ''
                    # Clean the number part: remove commas and percentage signs
                    trader_metrics['roi_per_period'] = roi_match.group(2).replace(',', '').replace('%', '')
                else:
                    trader_metrics['roi_value_sign'] = 'N/A'
                    trader_metrics['roi_per_period'] = raw_roi_value.replace(',', '').replace('%', '')
                i += 1
        # Check for "AUM" keyword.
        elif "AUM" in line:
            if i + 1 < len(lines):
                trader_metrics['aum_value'] = lines[i+1].replace(',', '') # Remove commas for numeric conversion
                i += 1
        # Check for "MDD" keyword.
        elif "MDD" in line:
            # Extract only the numerical part for 'period_days'
            match = re.search(r'(\d+)', line)
            if match and trader_metrics['period_days'] == 'N/A': # Set period_days only if not already set
                trader_metrics['period_days'] = match.group(1)

            if i + 1 < len(lines):
                trader_metrics['mdd_per_period'] = lines[i+1].replace('%', '') # Remove percentage sign
                i += 1
        # Check for "Sharpe Ratio" keyword.
        elif "Sharpe Ratio" in line:
            if i + 1 < len(lines):
                trader_metrics['sharpe_ratio_value'] = lines[i+1]
                i += 1
        # Check for "Mock" or "Live" keyword. These indicate the trader's status.
        # Assume the line immediately following this status is the copy capability.
        elif "Mock" in line: # Note: "or 'Live' in line" was removed here
            trader_metrics['mock_status'] = line
            # If there's a next line, assume it's the copy capability, regardless of its content.
            if i + 1 < len(lines):
                trader_metrics['copy_capability'] = lines[i+1]
                i += 1 # Consume this line as well, since it's now processed as copy_capability
        
        i += 1 # Move to the next line for the next iteration

    return trader_metrics
    
# --- Added function to extract trader details ---
# def get_trader_details(driver, trader_card_class, selector_classes):
#     """
#     Extracts trader names, PnL, ROI, and follower counts from card elements.

#     :param driver: WebDriver instance.
#     :param card_class: Class of the main card element (e.g., "card-outline").
#     :param selector_classes: A list containing:
#                              [0] Class of the element containing the trader's name (e.g., "typography-subtitle6").
#                              [1] Class for PnL data (e.g., "pnl-data").
#                              [2] Class for ROI data (e.g., "typography-subtitle3").
#                              [3] Class for link of the trader details-page (e.g., "inline-flex").
#     :return: A list of dictionaries, each containing 'name', 'pnl', 'roi'.
#     """
#     trader_data = []
#     card_elements = driver.find_elements(By.CLASS_NAME, trader_card_class)
#     print(f"Found {len(card_elements)} trader cards.")

#     # Extract selectors from the list
#     name_class = selector_classes[0]
#     pnl_class = selector_classes[1]
#     roi_class = selector_classes[2]
#     link_class = selector_classes[3]

#     for i, card in enumerate(card_elements):
#         name = "N/A"
#         pnl = "N/A"
#         roi = "N/A"
#         link = "N/A"

#         try:
#             # Extract trader name
#             name_element = card.find_element(By.CLASS_NAME, name_class)
#             name = name_element.text.strip()
#         except NoSuchElementException:
#             print(f"Trader name not found in card {i+1}.")

#         try:
#             # Extract PnL
#             pnl_element = card.find_element(By.CLASS_NAME, pnl_class)
#             pnl = pnl_element.text.strip()
#         except NoSuchElementException:
#             print(f"PnL data not found in card {i+1}.")

#         try:
#             # Extract ROI
#             roi_element = card.find_element(By.CLASS_NAME, roi_class)
#             roi = roi_element.text.strip()
#         except NoSuchElementException:
#             print(f"ROI data not found in card {i+1}.")

#         try:
#             # Extract link
#             link_element = card.find_element(By.CLASS_NAME, link_class)
#             link = link_element.text.strip()
#         except NoSuchElementException:
#             print(f"Link data not found in card {i+1}.")

#         trader_data.append({"name": name, "pnl": pnl, "roi": roi, "link": link})
#     return trader_data