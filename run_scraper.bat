@echo off

REM Navigate to your project directory
cd /d "C:\Binance_scraping"

REM Activate the virtual environment
call "C:\Users\User\my_google_binance_env\Scripts\activate.bat"

REM Set Binance API keys as environment variables
REM IMPORTANT: Replace YOUR_BINANCE_API_KEY and YOUR_BINANCE_SECRET_KEY with your actual keys
set BINANCE_USERNAME=YOUR_BINANCE_USERNAME
set BINANCE_PASSWORD=YOUR_BINANCE_PASSWORD

REM Run your Python script
python scraping_mock.py

REM Deactivate the virtual environment (optional but good practice)
deactivate

REM Keep the console window open after script finishes (optional, remove for silent execution)
REM pause