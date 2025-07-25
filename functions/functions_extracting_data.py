import re

def extract_trader_info(section_text, logger_instance):
    """
    Extracts the trader's name and ROI from the provided section text block.
    """
    trader_name = "Not Found"
    roi_value = None

    # Спочатку витягуємо ROI, оскільки він часто має передбачувану структуру
    roi_pattern = r"ROI\s*([+\-]?\d+(?:\.\d+)?%)"
    roi_match = re.search(roi_pattern, section_text)
    if roi_match:
        roi_value = float(roi_match.group(1).replace('%', ''))
    # else:
        # logger_instance.warning(f"ROI not found in section text: {section_text[:100]}...")

    # Тепер витягуємо ім'я трейдера більш надійно
    lines = section_text.strip().split('\n')
    
    # Визначаємо відомі службові фрази, які не є іменами трейдерів
    service_phrases_patterns = [
        r"Copied on:", r"Copy", r"Stop Mock Trading", r"Net Copy Amount",
        r"ROI", r"Unrealized PNL \(USDT\)", r"P&L \(USDT\)", r"Rank", r"Total AUM"
    ]
    
    potential_name_lines = []
    
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line: # Пропускаємо порожні рядки
            continue
        
        # Перевіряємо, чи рядок є службовою фразою
        is_service_phrase = False
        for pattern in service_phrases_patterns:
            if re.search(pattern, stripped_line, re.IGNORECASE):
                is_service_phrase = True
                break
        
        if is_service_phrase:
            continue
            
        # Якщо ROI був знайдений і цей рядок містить згаданий ROI, пропускаємо його
        if roi_match and roi_match.group(0) in stripped_line:
            continue
            
        # Якщо рядок вже містить "ROI", "PnL", "Rank", то це, ймовірно, частина блоку даних, а не саме ім'я
        if re.search(r"ROI|PnL|Rank", stripped_line, re.IGNORECASE):
            continue

        potential_name_lines.append(stripped_line)

    # Ім'я трейдера, ймовірно, є першим невідфільтрованим, непорожнім рядком
    if potential_name_lines:
        trader_name = potential_name_lines[0]
    
    return trader_name, roi_value

def extract_trader_info_from_ongoing(section_text, logger_instance):
    """
    Вилучає ім'я трейдера та всі інші відповідні фінансові показники з наданого текстового блоку секції.
    Повертає словник з витягнутими даними.
    """
    data = {
        "trader_name": "Not Found",
        "copied_on": None,
        "portfolio_id": None,
        "margin_balance": None,
        "net_copy_amount": None,
        "realized_pnl": None,
        "unrealized_pnl": None,
        "profit_shared": None,
        "net_profit": None,
        "profit_sharing": None,
    }

    # Regex patterns for all fields
    # Using re.escape for literal strings to handle special characters like ()
    patterns = {
        "copied_on": r"Copied on:\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2})",
        "portfolio_id": r"Portfolio ID:\s*(\d+)",
        "margin_balance": r"Margin Balance \(USDT\)\s*([+\-]?[\d,\.]+)",
        "net_copy_amount": r"Net Copy Amount \(USDT\)\s*([+\-]?[\d,\.]+)",
        "realized_pnl": r"Realized PNL \(USDT\)\s*([+\-]?[\d,\.]+)",
        "unrealized_pnl": r"Unrealized PNL \(USDT\)\s*([+\-]?[\d,\.]+)",
        "profit_shared": r"Profit Shared \(USDT\)\s*([+\-]?[\d,\.]+)",
        "net_profit": r"Net Profit \(USDT\)\s*([+\-]?[\d,\.]+)",
        "profit_sharing": r"Profit Sharing\s*([+\-]?\d+(?:\.\d+)?%)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, section_text)
        if match:
            value = match.group(1)
            # Special handling for portfolio_id to keep it as string
            if key == "portfolio_id":
                data[key] = value
            # Convert to float if it's a percentage or a number with commas/multiple decimals
            elif '%' in value:
                data[key] = float(value.replace('%', ''))
            elif re.match(r"^[+\-]?\d{1,3}(,\d{3})*(\.\d+)?$", value): # Handles 1,000.00
                data[key] = float(value.replace(',', ''))
            else:
                try:
                    data[key] = float(value) # Try converting to float for other numbers
                except ValueError:
                    data[key] = value # Keep as string if not a number
        else:
            logger_instance.warning(f"{key.replace('_', ' ').title()} not found in section text: {section_text[:100]}...")

    # Extract trader name - more refined
    lines = section_text.strip().split('\n')
    # Updated service phrases for more robust filtering
    service_phrases_patterns = [
        r"Copied on:", r"Portfolio ID:", r"Adjust Balance", r"Settings", r"Stop Copying",
        r"Fixed Ratio", r"Net Copy Amount \(USDT\)", r"Margin Balance \(USDT\)",
        r"Realized PNL \(USDT\)", r"Unrealized PNL \(USDT\)", r"Profit Shared \(USDT\)",
        r"Net Profit \(USDT\)", r"Profit Sharing", r"Expand Details", r"\|", # Common separators/buttons
        r"Copy", r"Stop Mock Trading", r"ROI", r"P&L", r"Rank", r"Total AUM" # General service terms
    ]
    
    potential_name_lines = []
    
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line: # Skip empty lines
            continue
        
        # Check if line is a service phrase
        is_service_phrase = False
        for pattern in service_phrases_patterns:
            if re.search(pattern, stripped_line, re.IGNORECASE):
                is_service_phrase = True
                break
        
        # Check if line is an extracted value (e.g., "10.0000", "-34.45%", or a date string)
        is_extracted_value = False
        for val_key, val in data.items():
            if val is not None and str(val) in stripped_line:
                is_extracted_value = True
                break
        
        if is_service_phrase or is_extracted_value:
            continue
            
        potential_name_lines.append(stripped_line)

    # The trader's name is likely the first non-filtered, non-empty line
    if potential_name_lines:
        trader_name = potential_name_lines[0]
        if not trader_name: # If after all filters, it's still empty or just spaces
            trader_name = "Not Found"
    
    data["trader_name"] = trader_name
    
    return data