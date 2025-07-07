from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
import pandas as pd 

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
        product_links = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.product-item'))
        )
        # time.sleep(2)  # Allow time for the page to load
        return [link.get_attribute("href") for link in product_links]
    except TimeoutException:
        print(f"⚠️ No products found at: {url}")
        return []

def scroll_to_bottom(driver):
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)

def extract_information(driver,data):
    print("Extracting product information...")
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
                    elif key == "Xuất xứ thương hiệu":
                        data['brand_originary'] = value
                    elif key == "Thời gian bảo hành":
                        data['guarantee'] = value
                    elif key == "Chất liệu":
                        data['materials'] = value
                    elif key == "Kích thước":
                        data['size'] = value
                    elif key == "Model":
                        data['model'] = value
    except TimeoutException:
        print("❌ 'Thông tin chi tiết' not found for this product.")
    
    return data

def scrape_product_data(driver,url):
    data = {key:None for key in ['title','url','variants','category','sub_category', 'brand','brand_originary','guarantee_time','materials','size','model']}
    data['url'] = url
    data['variants']=[]
    try:
        #title
        h1 = driver.find_element(by=By.TAG_NAME,value='h1').text 
        print(f'Title: {h1}')
        data['title'] = h1

        #color options
        try:
            #having color 
            color_container = driver.find_element(by=By.CSS_SELECTOR, value='div.sc-a7225a84-2.bMDykB') #parent div of color options
            div_container = color_container.find_elements(by=By.CSS_SELECTOR, value='div[data-view-id="pdp_main_select_configuration_item"]') #child divs of color options

            for i,div in enumerate(div_container, start=1):
                try: 
                    selected_color = div.find_element(By.CLASS_NAME,'selected-indicator').is_displayed()
                    if selected_color:
                        print(f"[DEBUG]: Color option {i} is selected")
                        time.sleep(3)
                        img_tag = driver.find_element(By.CSS_SELECTOR, 'div[data-view-id="pdp_main_view_gallery"] img')
                        current_img = img_tag.get_attribute("srcset")
                        active_color = color_container.find_element(By.CSS_SELECTOR, 'div.active span').text
                        price = driver.find_element(By.CSS_SELECTOR, 'div.product-price')
                        price_value = price.find_element(By.CLASS_NAME, 'product-price__current-price').text
                        data['variants'].append({'color': active_color, 
                                            'img_url': current_img, 
                                            'price': price_value})
                    else:
                        div.click()
                        print(f"[DEBUG]: Color option {i} is not selected, clicked to select it.")
                        time.sleep(1)
                        img_tag = driver.find_element(By.CSS_SELECTOR, 'div[data-view-id="pdp_main_view_gallery"] img')
                        current_img = img_tag.get_attribute("srcset")
                        active_color = color_container.find_element(By.CSS_SELECTOR, 'div.active span').text
                        price = driver.find_element(By.CSS_SELECTOR, 'div.product-price')
                        price_value = price.find_element(By.CLASS_NAME, 'product-price__current-price').text
                        data['variants'].append({'color': active_color, 
                                            'img_url': current_img, 
                                            'price': price_value})
                    # print(data['variants'])
                except NoSuchElementException:
                    # print(f"❌ Color option {i} not found.")
                    continue
                finally:
                    category = driver.find_element(by=By.XPATH,value='//*[@id="__next"]/div[2]/main/div/div[1]/div/a[3]').text
                    sub_category = driver.find_element(by=By.XPATH,value='//*[@id="__next"]/div[2]/main/div/div[1]/div/a[4]').text
                    data['category'] = category
                    data['sub_category'] = sub_category
        except Exception as e:
            # print(f"❌ No color options found: {e}")
            img_tag = driver.find_element(By.CSS_SELECTOR, 'div[data-view-id="pdp_main_view_gallery"] img')
            current_img = img_tag.get_attribute("srcset")
            category = driver.find_element(by=By.XPATH,value='//*[@id="__next"]/div[2]/main/div/div[1]/div/a[3]').text
            sub_category = driver.find_element(by=By.XPATH,value='//*[@id="__next"]/div[2]/main/div/div[1]/div/a[4]').text
            price = driver.find_element(By.CSS_SELECTOR, 'div.product-price')
            price_value = price.find_element(By.CLASS_NAME, 'product-price__current-price').text
            data['variants'].append({'color': None, 
                                    'img_url': current_img, 
                                    'price': price_value})
            data['category'] = category
            data['sub_category'] = sub_category

    except Exception as e:
        print(f"❌ Error while scraping product data: {e}")
    finally:
        data = extract_information(driver, data)
    # print("Data extracted successfully\n",data)
    
    return data

def get_all_product_urls(driver, url_list):
    all_data = []
    for i,url in enumerate(url_list,start=1):
        # print(f"Scraping product: {url}")
        driver.get(url)
        time.sleep(2)  # Allow time for the page to load
        data =scrape_product_data(driver, url)
        all_data.append(data)
        print("Append data to all_data")
        

    return all_data

def save_to_csv(data, filename='products.csv'):
    """
    Save the scraped data to a CSV file.
    :param data: List of dictionaries containing product data
    :param filename: Name of the output CSV file
    """
    flattened_data = []
    for product in data:
        variants = product.get('variants', [])
        for variant in variants:
            raw_price = variant.get('price', '')
            try:
                # Remove ₫ and dot separator, convert to int
                price_value = int(raw_price.replace('₫', '').replace('.', '').strip())
                formatted_price = f"{price_value:,.0f}".replace(",", ".") 
            except (ValueError, AttributeError):
                formatted_price = raw_price

            flat_product = {
                'title': product.get('title'),
                'url': product.get('url'),
                'color': variant.get('color'),
                'img_url': variant.get('img_url'),
                'price': formatted_price,
                'category': product.get('category'),
                'sub_category': product.get('sub_category'),
                'brand': product.get('brand'),
                'brand_originary': product.get('brand originary'),
                'guarantee_time': product.get('gurantee time'),
                'materials': product.get('materials'),
                'size': product.get('size'),
                'model': product.get('model'),
                
            }
            flattened_data.append(flat_product)
        

    df = pd.DataFrame(flattened_data)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    driver = initialize_driver()
    url = 'https://tiki.vn/dien-gia-dung/c1882'  # Category page URL
    product_urls = get_product_urls(driver, url)
    all_data = get_all_product_urls(driver, product_urls)
    # print(all_data)
    save_to_csv(all_data, 'products.csv')
    driver.quit()