# SCRAPING de IDEALISTA
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent

# Utility function to get element text safely
def safe_get_text(element, class_name):
    return element.find('span', class_=class_name).get_text() if element.find('span', class_=class_name) else None

# Generate a random user agent using fake_useragent
ua = UserAgent()
user_agent = ua.random

# Start undetected Chrome driver
options = uc.ChromeOptions()
options.add_argument(f'user-agent={user_agent}')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-blink-features=AutomationControlled')

# Run in normal (non-headless) mode to avoid detection
driver = uc.Chrome(options=options)

# List to store property data
properties = []

try:
    # Loop through the first 31 pages
    for page in range(1, 32):
        url = f'https://www.idealista.com/en/venta-viviendas/barcelona/eixample/la-dreta-de-l-eixample/pagina-{page}.htm' if page > 1 else 'https://www.idealista.com/en/venta-viviendas/barcelona/eixample/la-dreta-de-l-eixample/'
        
        try:
            driver.get(url)
            print(f'\nPage {page} loaded successfully')
            time.sleep(3)  # Wait for loading

            # Scroll to the bottom to ensure all content is loaded
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            # Wait until property info is loaded
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.item-info-container')))

            # Get the page source and parse it
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            n = 1
            for i in soup.find_all('div', class_="item-info-container"):
                print(f"Prop {n}, page {page}")
                
                title = i.find('a', class_="item-link")['title']
                link = 'https://www.idealista.com' + i.find('a', class_="item-link")['href']
                features = [span.get_text() for div in i.find_all('div', class_='item-detail-char') for span in div.find_all('span')]
                price_row = i.find('div', class_='price-row')
                price_sim = safe_get_text(price_row, 'item-price h2-simulated')
                price_down = safe_get_text(price_row, 'pricedown_price')
                tags = [span.get_text() for div in i.find_all('div', class_='listing-tags-container') for span in div.find_all('span')]
                description = i.find('div', class_='item-description').get_text() if i.find('div', class_='item-description') else None
                rooms = features[0] if len(features) > 0 else None
                size = features[1] if len(features) > 1 else None
                floor = features[2] if len(features) > 2 else None

                print(title)
                n += 1

                # Append property info to list of properties
                properties.append({
                   'Title': title,
                   'Description': description,
                   'Price_sim': price_sim,
                   'Price_down': price_down,
                   'Features': features,
                   'Tags': tags,
                   'Rooms': rooms,
                   'Size': size,
                   'Floor': floor,
                   'Link': link
                })

        except Exception as e:
            print(f"An error occurred on page {page}: {e}")

finally:
    driver.quit()  # Ensure the driver is closed

# Convert to DataFrame
df = pd.DataFrame(properties)

if not df.empty:
    # Export to Excel
    path = 'C:/Users/Julian/Downloads'
    filename = 'idealista_eixample.xlsx'
    df.to_excel(f'{path}/{filename}', index=False)
    print(f"Data exported to {path}/{filename}")
else:
    print("No data to export.")
