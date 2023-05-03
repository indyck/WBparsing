import requests
from bs4 import BeautifulSoup 
import gspread
from requests.exceptions import MissingSchema
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import InvalidArgumentException


mobile_emulation = { "deviceName": "iPhone X" }
options = webdriver.ChromeOptions()
options.add_experimental_option("mobileEmulation", mobile_emulation)
options.add_argument('--headless') 
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

gc = gspread.service_account(filename=r'utopian-medium-385118-f5b522b7c908.json')
driver = webdriver.Remote( command_executor='https://b2f8d940-b538-49db-ae52-630ac5a17484@chrome.browserless.io/webdriver',
    desired_capabilities=options.to_capabilities(), options=options)
sh = gc.open("Копия Расчеты себестоимости товаров")
worksheets = sh.worksheets()
for worksheet in worksheets[1::]:
    values_list = worksheet.col_values(3)

    for url in values_list[1::]:
        try:
            driver.get(url)
            driver.maximize_window()
            discount_button = WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.XPATH, '//del[@class="price-block__old-price j-wba-card-item-show"]')))
            element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//del[@class="price-block__old-price j-wba-card-item-show"]')))
            driver.execute_script("arguments[0].scrollIntoView();", element)
            discount_button.click()
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//span[@class="discount-tooltipster-value"]')))
            price = driver.find_element(By.XPATH, '//span[@class="discount-tooltipster-value"]').text
            price = price[:-1]
            price = price.replace(' ','')
            worksheet.update(f'D{values_list.index(url)+1}', price)
            print(worksheets.index(worksheet)+1, values_list.index(url)+1)
            
            
        except TimeoutException:
            try:
                price2 = driver.find_element(By.XPATH, '//ins[@class="price-block__final-price"]').text
                price2 = price2[:-1]
                price2 = price2.replace(' ', '')
                worksheet.update(f'D{values_list.index(url)+1}', price2)
                print(worksheets.index(worksheet)+1, values_list.index(url)+1)
                
            except NoSuchElementException:
                try:
                    driver.find_element(By.XPATH, '//span[@class="sold-out-product__text"]')
                    worksheet.update(f'D{values_list.index(url)+1}', 'нет в наличии')
                    print(worksheets.index(worksheet)+1, values_list.index(url)+1)
                #try:
                    # for i in range(3):
                    #     driver.find_element(By.TAG_NAME, "body").send_keys(Keys.DOWN)
                    # price3 = driver.find_element(By.XPATH, '//span[@class="qn0"]').text
                    # if price3 == '':
                    #     worksheet.update(f'D{values_list.index(url)+1}', 'нет в наличии')
                    # else:
                    #     price3 = price3[:-1]
                    #     price3.replace(' ', '')
                    #     worksheet.update(f'D{values_list.index(url)+1}', price3)
                    
                except NoSuchElementException:
                    print(worksheets.index(worksheet)+1, values_list.index(url)+1)
                    continue
                
        except InvalidArgumentException:
            print(worksheets.index(worksheet)+1, values_list.index(url)+1)
            continue
            