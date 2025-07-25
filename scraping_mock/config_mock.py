
none = None


URL_LOGIN = "https://accounts.binance.com/en/login"
URL_COPY_MANAGEMENT = "https://www.binance.com/en/copy-trading/copy-management"
# COPY_MANAGEMENT_SECTION_DIV_SELECTOR = "div.copy-mgmt-wrap"
COPY_MANAGEMENT_SECTION_DIV_SELECTOR = "div.bn-flex.py-\\[24px\\]"
spreadsheet_name = "Binance mock"
worksheet_name = "9"
first_5 = "30d, ROI, Smart filter - OFF"
# first_5 = "7d, ROI, Smart filter - OFF"
last_5 = "7d, ROI, Smart filter - ON"

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
    },
    "modal_confirm": {
        "selector_type":    "css selector", # Тип селектора для By.CSS_SELECTOR
        "selector_name":    "div.bn-modal-wrap, div.bs-modal"
    },
    "security_verification": {
        "selector_type":    "class name", # Тип селектора для By.CSS_SELECTOR
        "selector_name":    "mfa-verify-page"
    }
}