@echo off

REM Navigate to your project directory
cd /d "C:\Binance_scraping\scraping_mock"

REM Activate the virtual environment
call "C:\python_projects\Binance_scraping\venv_binance\Scripts\activate.bat"

REM Run your Python script
python main.py

REM Deactivate the virtual environment (optional but good practice)
deactivate

REM Keep the console window open after script finishes (optional, remove for silent execution)
REM pause