import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from tempfile import mkdtemp


def find_element_with_fallback(driver, locators):
    for by, value in locators:
        try:
            return driver.find_element(by, value)
        except NoSuchElementException:
            continue
    raise NoSuchElementException("Element not found with any of the provided locators")


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
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    chrome_options.binary_location = "/opt/chrome/chrome-linux64/chrome"
    service = Service(
        executable_path="/opt/chrome-driver/chromedriver-linux64/chromedriver",
        service_log_path="/tmp/chromedriver.log",
    )
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Navigate to the NSE website
        driver.get("https://www.nseindia.com/")
        print("Page loaded")

        # Wait for the page to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("Body found")

        # Wait for the NIFTY 50 data to be present
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "graph_head"))
        )
        print("Graph head found")

        # Find elements with fallback options
        open_value = find_element_with_fallback(
            driver,
            [
                (By.ID, "open_value"),
                (By.CLASS_NAME, "openVal"),
                (
                    By.XPATH,
                    "//li[contains(@class, 'open')]/span[contains(@class, 'openVal')]",
                ),
            ],
        ).text

        high_value = find_element_with_fallback(
            driver,
            [
                (By.ID, "high_value"),
                (By.CLASS_NAME, "highVal"),
                (
                    By.XPATH,
                    "//li[contains(@class, 'high')]/span[contains(@class, 'highVal')]",
                ),
            ],
        ).text

        low_value = find_element_with_fallback(
            driver,
            [
                (By.ID, "low_value"),
                (By.CLASS_NAME, "lowVal"),
                (
                    By.XPATH,
                    "//li[contains(@class, 'low')]/span[contains(@class, 'lowVal')]",
                ),
            ],
        ).text

        results = {"Open": open_value, "High": high_value, "Low": low_value}
        print("Data extracted successfully")

    except TimeoutException:
        print("Timeout waiting for page to load")
        results = {"Error": "Timeout waiting for page to load"}
    except NoSuchElementException as e:
        print(f"Element not found: {str(e)}")
        results = {"Error": f"Element not found: {str(e)}"}
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        results = {"Error": str(e)}
    finally:
        # Print page source for debugging
        print("Page source:")
        print(driver.page_source)

        # Close the WebDriver
        driver.quit()

    return {"statusCode": 200, "body": results}
