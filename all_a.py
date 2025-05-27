from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

url = "https://www.binance.com/ru-UA/copy-trading"
popup_class = "bn-modal-wrap"
close_button_class = "bn-modal-header-next"
checkbox_selector = (By.CLASS_NAME, "bn-checkbox")

def close_popup_if_exists(driver, popup_class_name, close_button_class_name):
    try:
        popup = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, popup_class_name))
        )
        print("Popup window found.")
        close_button = WebDriverWait(driver, 10).until(
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
        checkbox = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(checkbox_locator)
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
        WebDriverWait(driver, 10).until(
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

if __name__ == "__main__":
    driver = webdriver.Chrome()
    driver.get(url)

    close_popup_if_exists(driver, popup_class, close_button_class)
    uncheck_checkbox(driver, checkbox_selector)

    all_links = []
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
        )
        link_elements = driver.find_elements(By.TAG_NAME, "a")
        for link_element in link_elements:
            try:
                link = link_element.get_attribute("href")
                if link:
                    all_links.append(link)
            except StaleElementReferenceException:
                print("Застаріле посилання на елемент <a>. Пропускаємо.")

    except TimeoutException:
        print("Не знайдено жодних посилань на сторінці протягом заданого часу.")
    finally:
        driver.quit()

    if all_links:
        print("Всі посилання на сторінці копітрейдингу:")
        for link in all_links:
            print(link)
    else:
        print("На сторінці не знайдено жодних посилань.")