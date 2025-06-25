
none = None


# COPY_MANAGEMENT_SECTION_DIV_SELECTOR = "div.copy-mgmt-wrap"
COPY_MANAGEMENT_SECTION_DIV_SELECTOR = "div.bn-flex.py-\\[24px\\]"
spreadsheet_name = "Binance mock"
worksheet_name = "4"
first_5 = "30d, ROI, Smart filter - ON"
# first_5 = "7d, ROI, Smart filter - OFF"
last_5 = "7d, ROI, Smart filter - OFF"

SELECTORS = {
    "input_name": {
        "selector_type":    "name",
        "selector_name":    "username"
    },
    "input_pass": {
        "selector_type":    "id",
        "selector_name":    "password-input"
    },
    "next_button": {
        "selector_type":    "class name",
        "selector_name":    "bn-button__primary"
    },
    "tab_mock": {
        "selector_type":    "id",
        "selector_name":    "bn-tab-Copy"
    }
}