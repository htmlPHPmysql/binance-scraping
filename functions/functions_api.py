import requests
from requests.exceptions import ConnectionError, Timeout, HTTPError, RequestException
import time

# --- Функція для виконання запиту до API з повторними спробами ---
def fetch_api_data_with_retries(api_url, headers, payload, page_num, max_attempts, delay_seconds):
    """
    Виконує POST-запит до API з логікою повторних спроб у разі мережевих або інших помилок запитів.

    Args:
        api_url (str): URL API для запиту.
        headers (dict): Заголовки HTTP-запиту.
        payload (dict): Тіло запиту JSON.
        page_num (int): Номер сторінки, для якої робиться запит (використовується для логування).
        max_attempts (int): Максимальна кількість спроб запиту.
        delay_seconds (int): Затримка в секундах між повторними спробами.

    Returns:
        dict or None: JSON-відповідь від API, якщо запит успішний після всіх спроб;
                      None, якщо всі спроби невдалі або виникла непереборна помилка.
    """
    current_attempt = 0
    success = False
    json_response_data = None # Змінна для зберігання успішної відповіді

    while current_attempt < max_attempts and not success:
        try:
            print(f"Спроба {current_attempt + 1}/{max_attempts} отримати дані для сторінки {page_num}...")
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=20) # Збільшив таймаут
            response.raise_for_status() # Викличе HTTPError для 4xx/5xx статусів

            json_response_data = response.json()
            success = True
            print(f"Дані для сторінки {page_num} успішно отримано.")
            break # Успішно отримали дані, виходимо з циклу повторних спроб

        except (ConnectionError, Timeout, RequestException) as e:
            # Перехоплюємо всі загальні помилки запитів (включаючи ConnectionResetError, NameResolutionError)
            print(f"Виникла мережева або інша помилка запиту для сторінки {page_num} на спробі {current_attempt + 1}: {e}")
            if current_attempt < max_attempts - 1:
                current_attempt += 1
                print(f"  Чекаю {delay_seconds} секунд перед наступною спробою...")
                time.sleep(delay_seconds)
            else:
                print(f"  Вичерпано всі {max_attempts} спроб для сторінки {page_num}. Не вдалося отримати дані.")
                success = False # Забезпечуємо, що success False
                break # Виходимо з циклу повторних спроб

        except Exception as e:
            # Захоплюємо будь-які інші непередбачені помилки під час запиту
            print(f"Виникла невідома помилка під час запиту для сторінки {page_num} на спробі {current_attempt + 1}: {e}")
            success = False
            break # Не повторюємо для невідомих помилок, це може бути щось фундаментальне
    
    if not success:
        print(f"Не вдалося отримати дані для сторінки {page_num} після всіх спроб.")
        return None # Повертаємо None, якщо дані не були отримані

    return json_response_data # Повертаємо отримані дані у випадку успіху
