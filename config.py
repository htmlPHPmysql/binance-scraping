# config.py
none = None

URL = "https://www.binance.com/en/copy-trading"
# Sometimes 45 secs not enaught, No redirect detected within 45 seconds
DATA_LOAD_TIMEOUT = 50 # Time of the expectation data loding (in secs)
delay_sec_min = 5
delay_sec_max = 10
OUTPUT_FILENAME = "binance_copy_trading_dom.txt"
popup_class = "bn-modal-wrap"
close_button_class = "bn-modal-header-next"
checkbox_selector = "bn-checkbox"
pages_selector = "bn-pagination-item"
name_trader_class = "typography-subtitle6"
loading_indicator_class="animate-pulse"
TRADER_CARD_CLASS = "card-outline"
SELECTOR_CLASSES = [
    "typography-subtitle6", #name of the trader
    "pnl-data", # PnL
    "typography-subtitle3", # ROI
    "inline-flex" # link of the trader details-page
]
