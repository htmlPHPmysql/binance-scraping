import re

def extract_trader_info(section_text):
    """
    Extracts the trader's name and ROI from the provided section text block.
    Вилучає ім'я трейдера та ROI з наданого текстового блоку секції.
    """
    trader_name = "Not Found" # Default value if not found
    roi = "Not Found" # Default value if not found

    # Regex to find the trader's name:
    # Captures any text from the start of the string (^) until one of the keywords or a newline.
    # Uses re.DOTALL to allow '.' to match newlines for multi-line names.
    # The (?:...) is a non-capturing group.
    trader_name_match = re.search(r"^(.*?)(?:Copied on:|Net Copy Amount|ROI|\n)", section_text, re.DOTALL)
    if trader_name_match:
        # Get the captured group and clean up leading/trailing whitespace.
        trader_name = trader_name_match.group(1).strip()
        # Further clean up any leading numbers or known service words that might get caught.
        trader_name = re.sub(r"^\d+\s*", "", trader_name).strip()
        # Remove known service phrases like "Copy", "Stop Mock Trading" etc., case-insensitive.
        trader_name = re.sub(r"(?i)\b(Copy|Stop Mock Trading|Net Copy Amount|ROI|Unrealized PNL)\b.*", "", trader_name).strip()


    # Regex to find ROI:
    # Looks for "ROI" followed by optional whitespace (\s*)
    # Then captures an optional '+' or '-' sign, followed by one or more digits,
    # optionally followed by a decimal point and more digits, and finally a literal '%' sign.
    roi_match = re.search(r"ROI\s*([+\-]?\d+(\.\d+)?%)", section_text)
    if roi_match:
        roi = roi_match.group(1) # Capture the entire ROI value
        roi = float(roi.replace('%', ''))

    return trader_name, roi