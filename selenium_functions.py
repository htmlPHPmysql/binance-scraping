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
    loading_indicator_class,
    trader_card_class
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

def uncheck_checkbox(driver, checkbox_locator):
    try:
        checkbox = WebDriverWait(driver, DATA_LOAD_TIMEOUT).until(
            EC.presence_of_element_located(checkbox_locator)
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
        WebDriverWait(driver, DATA_LOAD_TIMEOUT).until(
            EC.element_to_be_clickable(checkbox_locator)
        )
        aria_checked = checkbox.get_attribute("aria-checked")
        if aria_checked == "true":
            checkbox.click()
            print("Checkbox unchecked (after scrolling into view).")
            return True
        else:
            print("Checkbox is already unchecked.")
            return True
    except TimeoutException:
        print("Checkbox not found or not clickable within the timeout.")
        return False
    except NoSuchElementException:
        print("Checkbox element not found.")
        return False
    except StaleElementReferenceException:
        print("Checkbox element is stale.")
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
    trader_links = []
    try:
        # Знаходимо всі елементи div з заданим класом картки
        card_elements = driver.find_elements(By.CLASS_NAME, trader_card_class)
        for card in card_elements:
            try:
                # В кожній картці знаходимо посилання на профіль трейдера.  Припускаємо, що посилання знаходиться в тегу <a>.
                # Це може бути змінено, якщо структура вашого HTML відрізняється.
                a_tag = card.find_element(By.TAG_NAME, "a")
                link = a_tag.get_attribute("href")
                trader_links.append(link)
            except NoSuchElementException:
                print("Посилання на трейдера не знайдено в одній з карток.")
                # Якщо посилання не знайдено в картці, продовжуємо обробку інших карток
                continue
        print(f"{len(trader_links)} lead traders links are found")
    except NoSuchElementException:
        print(f"Елементи з класом '{trader_card_class}' не знайдено.")
    return trader_links

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