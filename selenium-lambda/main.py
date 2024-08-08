import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from tempfile import mkdtemp

def lambda_handler(event, context):
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-tools")
    chrome_options.add_argument("--no-zygote")
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument(f"--user-data-dir={mkdtemp()}")
    chrome_options.add_argument(f"--data-path={mkdtemp()}")
    chrome_options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    chrome_options.add_argument("--remote-debugging-pipe")
    chrome_options.add_argument("--verbose")
    chrome_options.add_argument("--log-path=/tmp")
    chrome_options.binary_location = "/opt/chrome/chrome-linux64/chrome"

    service = Service(
        executable_path="/opt/chrome-driver/chromedriver-linux64/chromedriver",
        service_log_path="/tmp/chromedriver.log"
    )

    driver = webdriver.Chrome(
        service=service,
        options=chrome_options
    )
    # Open a webpage
    driver.get('https://www.google.com')
    # Find the search box
    search_box = driver.find_element(By.NAME, 'q')
    # Enter a search query
    search_box.send_keys('OpenAI')
    # Submit the search query
    search_box.send_keys(Keys.RETURN)
    # Wait for the results to load
    time.sleep(2)
    # Get the results
    results = driver.find_elements(By.CSS_SELECTOR, 'div.g')
    # Print the titles of the results
    titles = [result.find_element(By.TAG_NAME, 'h3').text for result in results]
    # Close the WebDriver
    driver.quit()
    return {
        'statusCode': 200,
        'body': titles
    }