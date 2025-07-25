import os

none = None

# Credentials Postgre
USER="postgres",       # Ваш користувач PostgreSQL (зазвичай 'postgres')
PASSWORD="3113325650", # !!! Введіть свій пароль для користувача postgres
HOST="127.0.0.1",      # Адреса сервера бази даних (локальний комп'ютер)
PORT="5432",           # Порт PostgreSQL (за замовчуванням 5432)
DATABASE="trading_data" # Ім'я вашої бази даних

# Credentials Binance
BINANCE_USERNAME = os.getenv('BINANCE_USERNAME')
BINANCE_PASSWORD = os.getenv('BINANCE_PASSWORD')

# Google Sheets API Key
# Path to your service account JSON file
# Important: Keep this file secure and you should have already placed 'credentials/service_account_key.json' in your project root
GOOGLE_CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials', 'service_account_key.json')

# Telegram Bot Credentials (Retrieve from environment variables)
# How to get:
# 1. Talk to @BotFather on Telegram, create a new bot, and get your BOT_TOKEN.
# 2. Start a chat with your new bot.
# 3. Go to https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates (replace <YOUR_BOT_TOKEN>).
#    Find "chat":{"id":YOUR_CHAT_ID,...} in the JSON response.
# For Windows CMD: set TELEGRAM_BOT_TOKEN=your_bot_token
# For Windows PowerShell: $env:TELEGRAM_BOT_TOKEN='your_bot_token'
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')