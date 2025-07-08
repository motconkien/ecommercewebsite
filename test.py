#scrapping data 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
import pandas as pd 

driver = webdriver.Safari()
url = "https://tiki.vn/dien-gia-dung/c1882"

driver.get(url)

wait = WebDriverWait(driver, 10)  # wait up to 10 seconds
product_links = wait.until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.product-item'))
)

product_urls = [link.get_attribute("href") for link in product_links]
data_products =[]


for i, url in enumerate(product_urls):
    driver.get(url)
    time.sleep(3)
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)

    #product infor
    data = {key:None for key in ['title','url','color','price','img_url','category','sub_category', 'brand','brand originary','gurantee time','materials','size','model']}
    data['url'] = url
    try:
        h1 = driver.find_element(by=By.TAG_NAME,value='h1').text 
        print(f'Title: {h1}')
        data['title'] = h1
        try:
            color_container = driver.find_element(by=By.CSS_SELECTOR, value='div.sc-a7225a84-2.bMDykB') #parent div of color options
            div_container = color_container.find_elements(by=By.CSS_SELECTOR, value='div[data-view-id="pdp_main_select_configuration_item"]') #child divs of color options

            #colors processing product
            for i, div in enumerate(div_container, start=1):
                #idea: if the color is visible, get data else click on it to make it visible
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
                        data['color'] = active_color
                        data['img_url'] = current_img
                        data['price'] = price_value
                        time.sleep(2)
                    else:
                        div.click()
                        print(f"[DEBUG]: Color option {i} is not selected, clicked to select it.")
                        time.sleep(1)
                        img_tag = driver.find_element(By.CSS_SELECTOR, 'div[data-view-id="pdp_main_view_gallery"] img')
                        current_img = img_tag.get_attribute("srcset")
                        active_color = color_container.find_element(By.CSS_SELECTOR, 'div.active span').text
                        price = driver.find_element(By.CSS_SELECTOR, 'div.product-price')
                        price_value = price.find_element(By.CLASS_NAME, 'product-price__current-price').text
                        data['color'] = active_color
                        data['img_url'] = current_img
                        data['price'] = price_value

                except Exception as e:
                    print(f"❌ Error for color option {i}: {e}")
                finally:
                    category = driver.find_element(by=By.XPATH,value='//*[@id="__next"]/div[2]/main/div/div[1]/div/a[3]').text
                    sub_category = driver.find_element(by=By.XPATH,value='//*[@id="__next"]/div[2]/main/div/div[1]/div/a[4]').text
                    data['category'] = category
                    data['sub_category'] = sub_category

        except Exception as e: #when there is no color options
            print(f"❌ No color options found: {e}")
            img_tag = driver.find_element(By.CSS_SELECTOR, 'div[data-view-id="pdp_main_view_gallery"] img')
            current_img = img_tag.get_attribute("srcset")
            category = driver.find_element(by=By.XPATH,value='//*[@id="__next"]/div[2]/main/div/div[1]/div/a[3]').text
            sub_category = driver.find_element(by=By.XPATH,value='//*[@id="__next"]/div[2]/main/div/div[1]/div/a[4]').text
            price = driver.find_element(By.CSS_SELECTOR, 'div.product-price')
            price_value = price.find_element(By.CLASS_NAME, 'product-price__current-price').text
            data['img_url'] = current_img
            data['price'] = price_value
            data['category'] = category
            data['sub_category'] = sub_category
    
        finally:
            print("Product information:")
            try:
                detail_section = WebDriverWait(driver, 10).until(
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
                                data['brand originary'] = value
                            elif key == "Bảo hành":
                                data['gurantee time'] = value
                            elif key == "Chất liệu":
                                data['materials'] = value
                            elif key == "Kích thước":
                                data['size'] = value
                            elif key == "Model":
                                data['model'] = value
            except TimeoutException:
                print("❌ 'Thông tin chi tiết' not found for this product.")

        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    print(f"Data for product {i+1}: {data}")
    
driver.quit()

# ✅ Save to CSV
df = pd.DataFrame(data_products)
df.to_csv("products_data.csv", index=False)