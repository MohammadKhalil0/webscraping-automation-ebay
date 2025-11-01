import time
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Set up Selenium WebDriver with headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open the eBay Global Tech Deals page
driver.get("https://www.ebay.com/globaldeals/tech")
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.ID, "refit-spf-container")))

# Scroll to the bottom of the page to trigger lazy loading
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)  # Allow time for content to load
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Wait for all product elements to be loaded
wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.dne-itemtile")))

# Extract product details
data = []
product_elements = driver.find_elements(By.CSS_SELECTOR, "div.dne-itemtile")

for product in product_elements:
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            title_element = product.find_element(By.CSS_SELECTOR, "h3.dne-itemtile-title")
            title = title_element.text.strip() if title_element else "N/A"
        except:
            title = "N/A"
        try:
            price_element = product.find_element(By.CSS_SELECTOR, "span.first")
            price = price_element.text.strip() if price_element else "N/A"
        except:
            price ="N/A"

        try:
            original_price_element = product.find_element(By.CSS_SELECTOR, "span.itemtile-price-strikethrough")
            original_price = original_price_element.text.strip() if original_price_element else "N/A"
        except:
            original_price = "N/A"

        try:
            shipping_element = product.find_element(By.XPATH, ".//span[contains(text(), 'shipping') or contains(text(), 'Shipping')]")
            shipping = shipping_element.text.strip()
        except:
            shipping = "N/A"
        try:
            item_url_element = product.find_element(By.CSS_SELECTOR, "a")
            item_url = item_url_element.get_attribute("href") if item_url_element else "N/A"
        except:
            item_url = "N/A"
        data.append([timestamp, title, price, original_price, shipping, item_url])
    except Exception as e:
        print(f"Error extracting product: {e}")

# Close the browser
driver.quit()

# Save data to CSV
csv_file = "ebay_tech_deals.csv"
header = ["timestamp", "title", "price", "original_price", "shipping", "item_url"]

with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    if file.tell() == 0:
        writer.writerow(header)  # Write header only if file is empty
    writer.writerows(data)

print(f"Scraped {len(data)} products and saved to {csv_file}.")
