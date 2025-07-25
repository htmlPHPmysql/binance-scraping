import requests
from requests.exceptions import ConnectionError, Timeout, HTTPError, RequestException
import psycopg2
from psycopg2 import Error
import time
import random # For random delays

from config_api import (
        none
    ,   API_URL
    ,   TOTAL_ITEMS
    ,   PAGE_SIZE
    ,   BATCH_SIZE
    ,   portfolio_type
    ,   trader_links_batch
    ,   trader_metrics_batch
    ,   trader_performance_batch
) # import variables form config_api.py

from config_sql import (
        none
    ,   trader_data_table_name
    ,   trader_data_table_columns
    ,   trader_metrics_table_name
    ,   trader_metrics_table_columns
    ,   trader_performance_table_name
    ,   trader_performance_table_columns
) # import variables form config_sql.py

from functions.sql_functions import (
    # add_trader_data,
    get_db_connection,
    create_table,
    insert_multiple_trader_links_batch,
    insert_multiple_batch,
    insert_trading_data,
    db_close_connection
) # Import SQL functions

from functions.functions_api import (
    fetch_api_data_with_retries,
) # Import API functions

# Period is usually fixed for these leaderboards, e.g., 30 Days
period_days = '180' # Assuming fixed 30 Days based on your previous data

# --- Helper for data cleaning/conversion (shared logic for preparing data) ---

def clean_and_convert_numeric(value, target_type):
    """
    Cleans and converts a string value to a numeric type (int or float).
    Handles 'N/A', '–', commas, and percentage signs. Returns None on invalid input.
    """
    # If the value is already a number (from API response), return it directly
    if isinstance(value, (int, float)):
        return value

    if not isinstance(value, str):
        return None # Or handle as per your default for non-string, non-numeric

    cleaned_value = value.strip()
    cleaned_value = cleaned_value.replace(',', '').replace('%', '').replace('–', '')

    if not cleaned_value:
        return None
    
    try:
        if target_type == int:
            return int(float(cleaned_value)) # Convert to float first to handle decimals like '1.0'
        elif target_type == float:
            return float(cleaned_value)
    except ValueError:
        return None
    return None

# --- Function for parsing the JSON response ---

def parse_api_response_for_traders(json_data: dict) -> list[dict]:
    """
    Parses the JSON response from the API to extract trader data.
    Maps API fields to the dictionary structure expected by our database insertion functions.
    """
    traders_data = []
    # print(json_data)
    try:
        # Navigate the JSON structure to find the list of traders
        trader_list = json_data.get('data', {}).get('list', [])

        for item in trader_list:
            # Extract and map fields from the API response item
            trader_id = item.get('leadPortfolioId')
            name = item.get('nickname')
            
            # Use avatarUrl directly from the API response
            profile_avatar_url = item.get('avatarUrl') # Changed from 'link' to 'avatarUrl'
            
            active_followers = item.get('currentCopyCount')
            total_spots = item.get('maxCopyCount')
            
            # API availability: based on 'apiKeyTag' being null or not
            api_availability = item.get('apiKeyTag')

            # badgeName: based on 'badgeName' being null or not
            badge_name = item.get('badgeName')

            # PnL Value and Sign
            pnl_value = item.get('pnl')
            # pnl_value_sign = '+' if pnl_value is not None and pnl_value >= 0 else '-'
            pnl_per_period = str(abs(pnl_value)) if pnl_value is not None else 'N/A'

            # ROI Value and Sign
            roi_value = item.get('roi')
            # roi_value_sign = '+' if roi_value is not None and roi_value >= 0 else '-'
            roi_per_period = str(abs(roi_value)) if roi_value is not None else 'N/A'

            # AUM Value
            aum_value = str(item.get('aum', 'N/A'))

            # MDD Value (directly a float/decimal in API)
            mdd_value = item.get('mdd')
            mdd_per_period = str(mdd_value) if mdd_value is not None else 'N/A'

            win_rate = item.get('winRate')
            win_rate_per_period = str(win_rate) if win_rate is not None else 'N/A'

            # Sharpe Ratio Value (note the key 'sharpRatio' in JSON)
            sharpe_ratio_value = str(item.get('sharpRatio', 'N/A')) # Use 'N/A' if null/not present

            # Mock Status (based on 'portfolioType')
            portfolio_type = item.get('portfolioType')

            # ROI evety day
            chart_items = item.get('chartItems')
            
            # Copy Capability - as 'copyStatus' is not in the provided JSON, default to 'N/A'
            # copy_capability = 'N/A' # Default to N/A as it's not present in sample JSON

            traders_data.append({
                'trader_id': trader_id,
                'name': name,
                'active_followers': active_followers,
                'total_spots': total_spots,
                'api_availability': api_availability,
                'period_days': period_days,
                # 'pnl_value_sign': pnl_value_sign,
                'pnl_per_period': pnl_per_period,
                # 'roi_value_sign': roi_value_sign,
                'roi_per_period': roi_per_period,
                'aum_value': aum_value,
                'mdd_per_period': mdd_per_period,
                'win_rate_per_period': win_rate_per_period,
                'sharpe_ratio_value': sharpe_ratio_value,
                'portfolioType': portfolio_type,
                'chartItems': chart_items,
                # 'copy_capability': copy_capability,
                'badgeName': badge_name,
                'avatarUrl': profile_avatar_url # Changed from 'link' to 'avatarUrl'
            })
    except (KeyError, TypeError) as e:
        print(f"Error parsing JSON response: Missing key or unexpected type - {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during JSON parsing: {e}")
        return []

    return traders_data


# --- Main Script Execution ---

if __name__ == "__main__":    
    print("API_URL: " + API_URL)    
        
    TOTAL_PAGES = (TOTAL_ITEMS + PAGE_SIZE - 1) // PAGE_SIZE
    print(f"TOTAL_PAGES: {TOTAL_PAGES}")  

    conn = get_db_connection()
    if not conn:
        print(f"Exiting due to database connection error \n{conn}")
        exit()
    else:
        print(f"Connection to PostgreSQL successfully established \n{conn}")

    try:
        # 1. Create all necessary tables first
        create_table(conn, trader_data_table_name, trader_data_table_columns)
        create_table(conn, trader_metrics_table_name, trader_metrics_table_columns)
        create_table(conn, trader_performance_table_name, trader_performance_table_columns)
        # create_trading_data_per_days(conn)
        

        print("\n--- Starting data scraping from API and insertion ---")

        for page_num in range(1, TOTAL_PAGES + 1):
            
            print(f"Fetching data for page {page_num}/{TOTAL_PAGES} from API with PAGE_SIZE={PAGE_SIZE}.")
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9,uk;q=0.8',
                'ClientType': 'web',
                'Referer': 'https://www.binance.com/copy-trading/leaderboard'
            }

            payload = {
                "pageNumber": page_num,
                "pageSize": PAGE_SIZE, 
                "timeRange": period_days + "D",
                "dataType": "PNL",
                "favoriteOnly": False,
                "hideFull": False,
                "nickname": "",
                "ord