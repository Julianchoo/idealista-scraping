# SCRAPING de IDEALISTA
# Imports
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup
import pandas as pd
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent

# Generate a random user agent using fake_useragent
ua = UserAgent()
user_agent = ua.random

# Start undetected Chrome driver
options = uc.ChromeOptions()
options.add_argument(f'user-agent={user_agent}')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-blink-features=AutomationControlled')

# How long to sleep
sleep_time = 3

# Run in normal (non-headless) mode to avoid detection
driver = uc.Chrome(options=options)

# List to store property data
properties = []

try:
    # Loop through the first 2 pages
    for page in range(1, 32):
        # Update the URL to include the page number
        if page == 1:
            url = 'https://www.idealista.com/en/venta-viviendas/barcelona/eixample/la-dreta-de-l-eixample/'
        else:
            url = f'https://www.idealista.com/en/venta-viviendas/barcelona/eixample/la-dreta-de-l-eixample/pagina-{page}.htm'
        try:
            # Load the URL
            driver.get(url)
            print('\n\n\n\n\n')
            print(f'Page {page} loaded successfully')
            time.sleep(sleep_time)  # Wait for loading

            # Scroll to the bottom of the page to ensure all content is loaded
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(sleep_time)  # Additional wait after scrolling

            # Wait for a known element to be present before proceeding
            # WebDriverWait(driver, sleep_time).until(
            #     EC.presence_of_element_located((By.CSS_SELECTOR, 'div.PostingCardLayout-sc-i1odl-0'))
            # )
            # print('Content found on the page')

            # Get the page source
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            #print(soup.prettify())

            #Scraping logic
            n=1
            for i in soup.find_all('div',class_="item-info-container"):
                print(f"Prop {n}, page {page}")
                #print(i.prettify())
                title = i.find('a', class_="item-link")['title']
                link = 'https://www.idealista.com'+i.find('a', class_="item-link")['href']
                features = [span.get_text() for div in i.find_all('div', class_='item-detail-char') for span in div.find_all('span')]
                price_row = i.find('div',class_='price-row')
                price_sim = price_row.find('span', class_='item-price h2-simulated').get_text() if price_row.find('span', class_='item-price h2-simulated') else None
                price_down = price_row.find('span', class_='pricedown_price').get_text() if price_row.find('span', class_='pricedown_price') else None
                tags = [span.get_text() for div in i.find_all('div', class_='listing-tags-container') for span in div.find_all('span')]
                description = i.find('div',class_='item-description').get_text() if i.find('div',class_='item-description') else None 
                rooms = features[0] if len(features) > 0 else None
                size = features[1] if len(features) > 1 else None
                floor = features[2] if len(features) > 2 else None
                print(title)
                print('\n')
                n=n+1    
        
                # Append property info to list of properties
                properties.append({
                   'Title':title
                   ,'Description':description
                   ,'Price_sim':price_sim
                   ,'Price_down':price_down 
                   ,'Features':features
                   ,'Tags':tags
                   ,'Rooms': rooms
                   ,'Size': size
                   ,'Floor': floor
                   ,'Link':link
                })
  
        except Exception as e:
            print(f"An error occurred on page {page}: {e}")

finally:
    driver.quit()  # Ensure the driver is closed after all iterations


# Convert to DataFrame
df = pd.DataFrame(properties)
print("DataFrame created")
print("\nDescription")
print(df.describe())
print("\nInfo")
print(df.info())
print("\nHead")
print(df.head)

# Export to Excel
path = 'C:/Users/Julian/Downloads'
filename = 'idealista_eixample.xlsx'
df.to_excel(f'{path}/{filename}', index=False)

print(f"Data exported to {path}/{filename}")