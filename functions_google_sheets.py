import os
import gspread

# Google Sheets API Key
# Шлях до вашого JSON-файлу сервісного акаунта
# Важливо: Зберігайте цей файл у безпечному місці та додайте 'credentials/' до .gitignore
GOOGLE_CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials', 'service_account_key.json')

def google_sheet_set_connection():
    """
    Authenticate with Google Sheets using the service account key
    Parameters: None
    Returns google connection
    """
    try:
        gc = gspread.service_account(filename=GOOGLE_CREDENTIALS_FILE)
        print("Google Sheets authentication successful.")
        return gc
    except FileNotFoundError:
        print(f"Error: Google Sheets credentials file not found at {GOOGLE_CREDENTIALS_FILE}")
        return # Exit the function if credentials file is missing
    except Exception as auth_e:
        print(f"Error during Google Sheets authentication: {auth_e}")
        return # Exit the function on authentication failure
        
def google_sheet_open_spreadsheet(gc, spreadsheet_name):
    """
    Open the specified spreadsheet by its name, with a check for success
    Parameters:
        1. google connection
        2. Name of the spreadsheet
    Returns google connection
    """
    try:
        spreadsheet = gc.open(spreadsheet_name)
        print(f"Successfully opened Google Spreadsheet: '{spreadsheet_name}'.")
        return spreadsheet
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"Error: Google Spreadsheet '{spreadsheet_name}' not found. Please ensure the name is correct and the service account has access.")
        return # Exit the function if spreadsheet not found
    except Exception as open_e:
        print(f"Error opening Google Spreadsheet '{spreadsheet_name}': {open_e}")
        return # Exit the function on other opening errors
    
def google_sheet_open_worksheet(spreadsheet, sheet_name):
    # Select the specific worksheet within the spreadsheet
    # Added a try-except for worksheet selection too
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
        print(f"Successfully selected worksheet: '{sheet_name}'.")
        return worksheet
    except gspread.exceptions.WorksheetNotFound:
        print(f"Worksheet '{sheet_name}' not found. Creating a new one...")
        try:
            # Add a new worksheet with the specified name
            # We'll initialize it with 1 row and 3 columns, suitable for headers.
            worksheet = spreadsheet.add_worksheet(sheet_name, rows=3, cols=4)
            print(f"Successfully created new worksheet: '{sheet_name}'.")
            return worksheet
        except Exception as create_e:
            print(f"Error creating new worksheet '{sheet_name}': {create_e}")
            return # Exit the function if worksheet creation fails
    except Exception as ws_e:
        print(f"Error accessing worksheet '{sheet_name}': {ws_e}")
        return # Exit the function on other worksheet errors
        
def write_to_google_sheet(timestamp, trader_name, roi, sum_roi, worksheet):
    try: 
        
        # Додаємо заголовки, якщо таблиця порожня
        if worksheet.row_count == 0 or worksheet.cell(3, 1).value is None: # 
            worksheet.insert_row(["Timestamp", "Trader name", "ROI, %", "Sum ROI"], 3)
        # else:
        #     print(f"Number of the rows: {worksheet.row_count}")
        #     print(f"Cell 3,1 is NOT empty: {worksheet.cell(3, 1).value}")
        
        # Додаємо новий рядок з даними
        # timestamp потрібно конвертувати у формат, зрозумілий Google Sheets (наприклад, ISO-формат)
        worksheet.append_row([timestamp.isoformat(), trader_name, roi, sum_roi])
        
        print(f"Data added successfully in Google Sheet: {timestamp.strftime('%Y-%m-%d %H:%M:%S')} {trader_name}")
    except Exception as e:
        print(f"Помилка при записі в Google Sheet: {e}")


