@echo off

REM Navigate to your project directory
cd /d "D:\python_projects\Binance_scraping\scraping_mock"

REM Activate the virtual environment
call "..\venv_binance\Scripts\activate.bat"

REM Перевіряємо, чи активовано віртуальне середовище (необов'язково, але корисно для відладки)
if defined VIRTUAL_ENV (
    echo Virtual enviarement is activated: %VIRTUAL_ENV%
) else (
    echo Помилка: Віртуальне середовище не активовано.
    goto :eof
)

REM Run your Python script
python main.py

REM Deactivate the virtual environment (optional but good practice)
deactivate

REM Keep the console window open after script finishes (optional, remove for silent execution)
pause