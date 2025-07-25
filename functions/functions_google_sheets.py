import os
import logging
import gspread
import gspread_formatting
# print(dir(gspread))
# print(f"Contents of gspread.utils: {dir(gspread.utils)}")
# print(f"Contents of gspread_formatting.util: {dir(gspread_formatting.util)}")
from gspread_formatting import (
    set_frozen,
    format_cell_range, 
    get_conditional_format_rules,
    ConditionalFormatRule, 
    BooleanRule, 
    CellFormat, 
    Color, 
    textFormat,
    GridRange,
    BooleanCondition
)

from credentials import (
        none # This line seems to be a placeholder, you can remove it if not needed in your actual credential.py
    ,   GOOGLE_CREDENTIALS_FILE
)

# Отримуємо логер, який вже налаштований у головному скрипті
logger = logging.getLogger(__name__)

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
    Returns spreadsheet
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
    """
    Select the specific worksheet within the spreadsheet by its name, with a check for success
    Parameters:
        1. Name of the spreadsheet
        2. Name of the worksheet
    Returns worksheet
    """
    # 
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

            worksheet.insert_row(["Timestamp", "Search params", "Trader name", "ROI, %", "Sum ROI"], 3)
            set_cell_color(worksheet, "3", "A:E", "#f5f5dc")
            print("Headers added")
            
            set_frozen(worksheet, rows=3)
            
            # # --- NEW: Apply Conditional Formatting Rules ---
            # rules = get_conditional_format_rules(worksheet)
            # rules.clear() # Clear all existing rules to avoid duplication on re-runs

            # # --- NEW RULE: Every fifth row in column E (e.g., light blue background) ---
            # red_format = CellFormat(backgroundColor=Color(1, 0, 0))
            # rules.append(ConditionalFormatRule(
            #     ranges=[GridRange.from_a1_range('E:E', worksheet)], # Apply to the entire column E
            #     booleanRule=BooleanRule(
                    
            #         condition=BooleanCondition('CUSTOM_FORMULA', ['=AND(E1<0; ROW()>=8; MOD(ROW()-3; 5)=0)']), # Condition: row number is a multiple of 5
            #         # condition=BooleanCondition('CUSTOM_FORMULA', ['=MOD(ROW(), 5)=0']), # does not functione because of localization
            #         format=red_format
            #     )
            # ))
            # green_format = CellFormat(backgroundColor=Color(0, 1, 0))
            # rules.append(ConditionalFormatRule(
            #     ranges=[GridRange.from_a1_range('E:E', worksheet)], # Apply to the entire column E
            #     booleanRule=BooleanRule(
                    
            #         condition=BooleanCondition('CUSTOM_FORMULA', ['=AND(E1>0; ROW()>=8; MOD(ROW()-3; 5)=0)']), # Condition: row number is a multiple of 5
            #         # condition=BooleanCondition('CUSTOM_FORMULA', ['=MOD(ROW(), 5)=0']), # does not functione because of localization
            #         format=green_format
            #     )
            # ))
            # rules.save()

            return worksheet
        except Exception as create_e:
            print(f"Error creating new worksheet '{sheet_name}': {create_e}")
            return # Exit the function if worksheet creation fails
    except Exception as ws_e:
        print(f"Error accessing worksheet '{sheet_name}': {ws_e}")
        return # Exit the function on other worksheet errors
        
def write_to_google_sheet(data_row, worksheet):
    """
    Create headers of the table if NO exist
    Insert data in the cells
    Parameters:
        1. Dictionary of the data
        2. Name of the worksheet
    Returns worksheet
    """
    try: 
        # --- DEBUGGING: Print gspread version ---
        # print(f"Using gspread version: {gspread.__version__}")
        # print(f"gspread loaded from: {gspread.__file__}")
        # --- END DEBUGGING ---

        # else:
        #     print(f"Number of the rows: {worksheet.row_count}")
        #     print(f"Cell 3,1 is NOT empty: {worksheet.cell(3, 1).value}")
        
        # Додаємо новий рядок з даними
        # timestamp потрібно конвертувати у формат, зрозумілий Google Sheets (наприклад, ISO-формат)
        timestamp       = data_row.get("Timestamp")
        params_search   = data_row.get("SearchParams")
        trader_name     = data_row.get("TraderName")
        roi_value       = data_row.get("ROIValue")
        roi_sum         = data_row.get("ROIsum")

        worksheet.append_row([timestamp.isoformat(), params_search, trader_name, roi_value, roi_sum])
        
        print(f"Data added successfully in Google Sheet: {trader_name} : {roi_value}")
    except Exception as e:
        print(f"Error during inserting in the Google Sheet: {e}")

def hex_to_rgb_normalized(hex_color):
    """
    Converts a hexadecimal color code (e.g., "#RRGGBB") to a tuple of normalized RGB values (0.0-1.0)
    Parameters:
        1. hex_color color in hex format    
    Returns tuple
    """
    hex_color = hex_color.lstrip('#')
    lv = len(hex_color)
    rgb = tuple(int(hex_color[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    return tuple(c / 255.0 for c in rgb)

def set_cell_color(worksheet, row_index, name_collomn, color_hex):
    """
    Coloring cells
    Parameters:
        1. Name of the worksheet
        2. Number of the row for coloring
        3. Collomn for coloring
        4. Data for choosing witch color
    Returns None
    """
    try: 
        # Getting number of the row
        # current_row_index = worksheet.row_count
        # print(f"current_row_index befor coloring cell: {current_row_index}")
        background_color = Color(*hex_to_rgb_normalized(color_hex))
        
        # Створюємо формат комірки
        cell_format = CellFormat(
            backgroundColor=background_color,
            textFormat=textFormat(bold=True) # Додатково робимо текст жирним
        )
        # Застосовуємо форматування до комірки ROI (стовпець 3)
        range_to_format = f"{name_collomn}{row_index}" # Наприклад, C2, C3, C4...
        format_cell_range(worksheet, range_to_format, cell_format)
    except Exception as e:
        print(f"Error during coloring cell in the Google Sheet: {e}")

def set_default_cell_color(worksheet, row_index):
    """
    Set default sell color
    Parameters:
        1. Name of the worksheet
    Returns none
    """
    try:
        
        # Getting number of the row
        new_row_index = row_index
        new_col_index = worksheet.col_count
        # Спочатку встановлюємо стандартний (наприклад, білий) фон для комірки ROI
        default_background_color = Color(1, 1, 1) # Білий колір
        default_cell_format = CellFormat(backgroundColor=default_background_color)
        range_to_format = f"A{new_row_index}:{new_col_index}{new_row_index}"
        format_cell_range(worksheet, range_to_format, default_cell_format)
        # print(f"Debug: Cells ({range_to_format}) setted to default background")
    except Exception as e:
        print(f"Error during coloring cell in the Google Sheet: {e}")

def get_last_data_row_index(worksheet):
    """
    Отримує індекс останнього рядка, який містить будь-які непорожні дані.
    Повертає 0, якщо аркуш повністю порожній.
    """
    all_values = worksheet.get_all_values() # Отримує всі значення з аркуша
    for i in range(len(all_values) - 1, -1, -1): # Ітерує по рядках, починаючи з останнього
        if any(cell.strip() for cell in all_values[i]): # Перевіряє, чи є в рядку хоча б одна непорожня комірка (після видалення пробілів)
            return i + 1 # Повертає 1-базований індекс рядка
    return 0 # Якщо всі рядки порожні, повертає 0 (для порожнього аркуша)

def auto_fit_columns(worksheet, start_column_index, end_column_index, logger_instance):
    """
    Automatically adjusts the width of columns in a Google Sheet worksheet.

    Args:
        worksheet (gspread.Worksheet): The worksheet object to modify.
        start_column_index (int): The 0-indexed starting column to auto-fit.
        end_column_index (int): The 0-indexed ending column to auto-fit (inclusive).
        logger_instance (logging.Logger): The logger instance from the main script.
    """
    local_logger = logger_instance if logger_instance else logging.getLogger(__name__)
    try:
        requests = [
            {
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": worksheet.id,
                        "dimension": "COLUMNS",
                        "startIndex": start_column_index,
                        "endIndex": end_column_index + 1 # end_index is exclusive in Sheets API
                    }
                }
            }
        ]
        worksheet.spreadsheet.batch_update({"requests": requests})
        local_logger.info(f"Columns {start_column_index} to {end_column_index} auto-fitted successfully.")
    except Exception as e:
        local_logger.error(f"Failed to auto-fit columns {start_column_index} to {end_column_index}: {e}", exc_info=True)
