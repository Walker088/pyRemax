from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOpts

opts = FirefoxOpts()
opts.add_argument("--headless")

delay = 5 # seconds
try:
    driver = webdriver.Firefox(options=opts)
    driver.get('https://google.com')
    myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.TAG_NAME, 'head')))
    print("Selenium Test Successed on https://google.com!")
except Exception as e:
    print(e)
finally:
    driver.close()
