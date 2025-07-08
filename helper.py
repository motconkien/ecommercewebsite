from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
import pandas as pd 
import re

def initialize_driver():
    """
    Initialize the Selenium WebDriver.
    returns : driver
    """
    driver = webdriver.Safari()
    return driver

def get_product_urls(driver, url):
    """
    Get product URLs from a category page.
    :param driver: Selenium WebDriver instance
    :param url: URL of the category page
    :return: List of product URLs
    """
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    try:
        time.sleep(2)  # Allow time for the page to load

        for _ in range(5):
            xem_them_btn = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/div/div/div[2]/div[2]/div[6]/div')
            xem_them_btn.click()
            time.sleep(2)  # Allow time for the page to load more products

        product_links = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.product-item'))
        )

        after_clicked = len([link.get_attribute("href") for link in product_links])
        print(f"After clicking: {after_clicked} products found.")
        return [link.get_attribute("href") for link in product_links]
    except TimeoutException:
        print(f"⚠️ No products found at: {url}")
        return []

def scroll_to_bottom(driver):
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)

def extract_information(driver,data):
    # print("Extracting product information...")
    #scroll 
    scroll_to_bottom(driver)

    try:
        detail_section = WebDriverWait(driver, 12).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[contains(., "Thông tin chi tiết")]')
            )
        )

        html = detail_section.get_attribute("innerHTML")
        soup = BeautifulSoup(html, "html.parser")

        rows = soup.find_all("div", class_="sc-34e0efdc-2 kAFhAU")
        for row in rows:
            items = row.find_all("div", class_="sc-34e0efdc-3 jcYGog")
            for item in items:
                spans = item.find_all("span")
                if len(spans) >= 2:
                    key = spans[0].get_text(strip=True)
                    value = spans[1].get_text(strip=True)
                    if key == "Thương hiệu":
                        data['brand'] = value
    except TimeoutException:
        print("❌ 'Thông tin chi tiết' not found for this product.")
        
    
    return data

def extract_description(driver,data):
    """
    Extract product description from the page.
    :param driver: Selenium WebDriver instance
    :param data: Dictionary to store product data
    :return: Updated data dictionary with description
    """
    scroll_to_bottom(driver)
    try:
        detail_section = WebDriverWait(driver, 12).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[contains(., "Mô tả sản phẩm")]')
            )
        )
        time.sleep(2)  # Allow time for the section to load
        html = detail_section.get_attribute("innerHTML")
        soup = BeautifulSoup(html, "html.parser")
        container  = soup.find('div', class_='sc-f5219d7f-0 haxTPb')
        allowed_tags = ['p', 'h3']

        filtered_texts = []
        for tag in container.find_all(allowed_tags):
            if not tag.find('img'):  # Skip if contains <img>
                text = tag.get_text(strip=True)
                if text:  # Make sure it’s not empty
                    filtered_texts.append(text)
        data['description'] = '\n'.join(filtered_texts).replace('AD', '')

    except NoSuchElementException:
        print("❌ Description not found for this product.")
        data['description'] = None
    except TimeoutException:
        print("❌ 'Mô tả sản phẩm' section not found for this product.")
        data['description'] = None
    
    return data


def scrape_product_data_new(driver, url):
    """
    Scrape product data from a given product URL.
    :param driver: Selenium WebDriver instance
    :param url: URL of the product page
    :return: Dictionary containing product data
    """
    data = {key:None for key in ['title','url','img_url','price','category','sub_category', 'brand', 'description','star','star_reviewers','sold']}
    data['url'] = url
    
    try:
        driver.get(url)
        time.sleep(2)

        # Title
        try:
            data['title'] = driver.find_element(By.TAG_NAME, 'h1').text
        except NoSuchElementException:
            pass

        # Image URL
        try:
            img_tag = driver.find_element(By.CSS_SELECTOR, 'div[data-view-id="pdp_main_view_gallery"] img')
            data['img_url'] = img_tag.get_attribute("srcset")
        except NoSuchElementException:
            pass

        # Price
        try:
            price_element = driver.find_element(By.CSS_SELECTOR, 'div.product-price')
            data['price'] = price_element.find_element(By.CLASS_NAME, 'product-price__current-price').text
        except NoSuchElementException:
            pass

        # Reviews & Sold
        try:
            container = driver.find_element(By.CSS_SELECTOR, 'div.sc-1a46a934-0.fHEkTS')
            data['star'] = container.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/div/div[2]/div[1]/div[1]/div[1]/div[2]/div/div[1]/div/div[1]/div[1]/div[2]/div/div[1]/div[1]').text
            data['star_reviewers'] = container.find_element(By.CSS_SELECTOR, 'a.number[data-view-id="pdp_main_view_review"]').text
            data['sold'] = driver.find_element(By.CSS_SELECTOR, 'div[data-view-id="pdp_quantity_sold"]').text
        except NoSuchElementException:
            pass

        # Category
        try:
            data['category'] = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/div/div[1]/div/a[3]').text
            data['sub_category'] = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/div/div[1]/div/a[4]').text
        except NoSuchElementException:
            pass

    except Exception as e:
        print(f"[DEBUG] ❌ Error scraping {url}: {e}")

    finally:
        # Extract additional info (still attempt even if scraping fails)
        data = extract_information(driver, data)
        data = extract_description(driver, data)

    return data

def get_all_product_urls(driver, url_list):
    all_data = []
    for i,url in enumerate(url_list,start=1):
        data =scrape_product_data_new(driver, url)
        all_data.append(data)
        print("Append data to all_data")

    return all_data

def clean_price(raw_price):
    # Remove currency symbol and dots, strip spaces
    try:
        price_value = int(raw_price.replace('₫', '').replace('.', '').strip())
        # Format number with dot as thousand separator (e.g. 1.234.567)
        formatted_price = f"{price_value:,}".replace(',', '.')
    except Exception as e:
        formatted_price = None
    return formatted_price

def clean_text(raw_text):
    """
    Clean the text string by removing unnecessary characters and whitespace.
    :param raw_text: String containing the text to be cleaned
    :return: Cleaned string
    """
    try:
        # Extract the number from the string (e.g., "1.234 đánh giá" -> 1234)
        return int(re.search(r'\d+', raw_text).group())
    except Exception as e:
        return 0  # Return 0 if parsing fails


def save_to_csv(data, filename='products.csv'):
    """
    Save the scraped data to a CSV file.
    :param data: List of dictionaries containing product data
    :param filename: Name of the output CSV file
    """
   
    df = pd.DataFrame(data)
    df['price'] = df['price'].apply(clean_price)
    df['star_reviewers'] = df['star_reviewers'].apply(clean_text)
    df['sold'] = df['sold'].apply(clean_text)
    df.to_csv(filename, index=False)
    # print(f"Data saved to {filename}")

if __name__ == "__main__":
    driver = initialize_driver()
    url = 'https://tiki.vn/dien-gia-dung/c1882'  # Category page URL
    product_urls = get_product_urls(driver, url)
    all_data = get_all_product_urls(driver, product_urls)
    # print(all_data)
    save_to_csv(all_data, 'products.csv')
    driver.quit()