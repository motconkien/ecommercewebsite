#scrapping data 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Safari()
url = "https://tiki.vn/dien-gia-dung/c1882"
driver.get(url)

wait = WebDriverWait(driver, 10)  # wait up to 10 seconds
product_links = wait.until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.product-item'))
)

for link in product_links:
    # print(link.get_attribute("href"))
    # print(link.get_attribute("class"))
    link.click()
    product_url = link.get_attribute('href')
    # print(product_url)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(5)

    #product infor
    data = {key:None for key in ['title','color','price']}
    try:
        h1 = driver.find_element(by=By.TAG_NAME,value='h1').text 
        # print(f'Title: {h1}')
        color_container = driver.find_element(by=By.CSS_SELECTOR, value='div.sc-a7225a84-2.bMDykB')
        div_container = color_container.find_elements(by=By.CSS_SELECTOR, value='div[data-view-id="pdp_main_select_configuration_item"]')
        for i, div in enumerate(div_container, start=1):
            try:
                # Get current image URL
                time.sleep(10)
                img_tag = driver.find_element(By.CSS_SELECTOR, 'div[data-view-id="pdp_main_view_gallery"] img')
                current_img = img_tag.get_attribute("srcset")

                # Scroll & click the color option
                driver.execute_script("arguments[0].scrollIntoView(true);", div)
                driver.execute_script("arguments[0].click();", div)
                print(f"\n{i}. ✅ Clicked color option")

                # # Wait until the image changes

                # Get updated image
                updated_img = driver.find_element(By.CSS_SELECTOR, 'div[data-view-id="pdp_main_view_gallery"] img').get_attribute("srcset")

                # Get the active color name *AFTER* it's active
                active_color = color_container.find_element(By.CSS_SELECTOR, 'div.active span').text

                print(f"   🎨 Color: {active_color}")
                print(f"   🖼️ Image URL: {updated_img}")
                time.sleep(2)

            except Exception as e:
                print(f"❌ Error for color option {i}: {e}")
            print("**" * 20)
        # color_options = wait.until(
        # EC.presence_of_all_elements_located(
        #     (By.CSS_SELECTOR, 'div[data-view-id="pdp_main_select_configuration_item"]')
        # ))

        # for i, color in enumerate(color_options, 1):
        #     driver.execute_script("arguments[0].scrollIntoView(true);", color)
        #     time.sleep(1)
        #     driver.execute_script("arguments[0].click();", color)
        #     time.sleep(2)

        #     # Check if clicked successfully
        #     class_name = color.get_attribute("class")
        #     color_name = color.find_element(By.TAG_NAME, "span").text

        #     img = driver.find_element(By.CSS_SELECTOR, 'img[data-view-id="pdp_main_image"]')
        #     img_url = img.get_attribute("src")

        #     print(f"{i}. Color: {color_name}")
        #     print(f"   Class: {class_name}")
        #     print(f"   Image URL: {img_url}")
        #     print("✅ Click success\n" if "active" in class_name else "❌ Click failed\n")

        # price = driver.find_element(by=By.CLASS_NAME, value='product-price__current-price')
        # description = driver.find_element(by=By.CSS_SELECTOR, value='div.sc-f5219d7f-0.haxTPb')
        # p_tags = description.find_elements(by=By.TAG_NAME,value='p')
        # text_des = ','.join([p.text for p in p_tags])
            
        # print(f"tilte: {h1}\nimg-link:{img}\nprice:{price}\ndescription:{text_des}")
    except Exception as e:
                print(f"An error occurred: {e}")  
    break

