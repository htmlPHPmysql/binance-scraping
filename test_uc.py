import undetected_chromedriver as uc
import time

try:
    options = uc.ChromeOptions()
    options.add_argument("--headless") # You can comment this out if you want to see the browser window
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = uc.Chrome(options=options)
    print("WebDriver initialized successfully!")

    driver.get("https://www.google.com")
    print(f"Opened: {driver.current_url}")
    time.sleep(5) # Give it some time to load
    print(f"Page title: {driver.title}")

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'driver' in locals() and driver:
        driver.quit()
        print("Browser closed.")