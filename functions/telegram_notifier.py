import requests
import logging

# Отримуємо логер, який вже налаштований у головному скрипті
logger = logging.getLogger(__name__)

def send_telegram_message(bot_token, chat_id, message_text):
    """
    Надсилає повідомлення в Telegram за допомогою Telegram Bot API.

    Args:
        bot_token (str): Токен вашого Telegram бота (отриманий від BotFather).
        chat_id (str): ID чату, куди надсилати повідомлення (ваш особистий ID чату з ботом).
        message_text (str): Текст повідомлення, яке потрібно надіслати.
    Returns:
        bool: True, якщо повідомлення надіслано успішно, False в іншому випадку.
    """
    # Додано .strip() для видалення зайвих пробілів/нових рядків з токена та chat_id
    cleaned_bot_token = bot_token.strip() if bot_token else None
    cleaned_chat_id = chat_id.strip() if chat_id else None

    if not cleaned_bot_token or not cleaned_chat_id:
        logger.warning("TELEGRAM_BOT_TOKEN або TELEGRAM_CHAT_ID не встановлені або порожні після очищення. Пропуск надсилання Telegram-повідомлення.")
        return False

    api_url = f"https://api.telegram.org/bot{cleaned_bot_token}/sendMessage"
    payload = {
        "chat_id": cleaned_chat_id,
        "text": message_text,
        "parse_mode": "HTML" # Дозволяє використовувати HTML форматування в повідомленнях (наприклад, <b>жирний</b>)
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status() # Викличе виняток для кодів стану HTTP 4xx/5xx
        json_response = response.json()
        if json_response.get("ok"):
            logger.info("Telegram message send successfully")
            return True
        else:
            logger.error(f"Помилка надсилання Telegram повідомлення: {json_response.get('description', 'Невідома помилка')}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Помилка мережі або запиту під час надсилання Telegram повідомлення: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"Неочікувана помилка під час надсилання Telegram повідомлення: {e}", exc_info=True)
        return False
