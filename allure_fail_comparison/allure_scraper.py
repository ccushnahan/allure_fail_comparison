
"""Small script to scrape json data from allure report output"""
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
import json
import pathlib
import os
import random
import re
import time
from lxml import html
from loguru import logger


def scrape_allure_report(report_url: str) -> list:
    """Scrapes allure report"""
    # set base url
    logger.debug("Setting default URL")
    base_url: str = report_url
    
    # setup driver
    logger.debug("Setting up webdriver instance")
    driver: webdriver = driver_setup()
    
    # open initial page and check test date
    logger.debug("Loading base page")
    open_page_webdriver(driver, base_url)

    logger.debug("Checking test run date")
    title: str = get_test_title(driver)
    date: str = get_test_run_date(title)

    logger.debug("Confirming date not scraped")
    if False: 
        logger.debug("Test run already scraped. Stopping scrape attempt.")
        exit()

    # Update base url and navigate to suite page
    logger.debug("Navigating to suite page")
    base_url: str = update_base_url(driver)
    suite_url: str = f"{base_url}#suites"
    open_page_webdriver(driver, suite_url)

    # Scrape test nodes UIDs
    logger.debug("Scraping failed test node UID numbers")
    test_uids: list = get_failed_test_uids(driver)
    if (len(test_uids) == 0):
        logger.debug("No failed tests completing scrape")
        exit()

    # scrape UID data
    logger.debug("Scraping data from UIDS")
    data: dict = scrape_uid_list_data(test_uids, base_url)

    # saving scraped data
    logger.debug("Saving scraped data")
    save_scrape_data_to_json(date, data)

    # Pass data on
    return [data, date, base_url]


def open_page_webdriver(driver: webdriver, url: str) -> None:
    """Opens page with selenium webdriver"""
    driver.get(url)
    time.sleep(2)

def open_page_requests(url: str) -> requests.Response:
    """Opens page using requests lib"""
    headers = set_headers()
    response = requests.get(url, headers=headers)
    return response

def set_headers():
    """Set the headers based on .env file"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    return headers

def get_test_title(driver: webdriver) -> str:
    """Gets the test title"""
    title_xpath = "//*[@class='widget__title']"
    page_source  = driver.page_source
    tree = html.fromstring(page_source)
    title = tree.xpath(title_xpath)[0].text
    return title

def get_test_run_date(title: str) -> str:
    """Gets date from title"""
    match = re.search("\d\d[/]\d\d[/]\d\d\d\d", title)
    return match.group()

def get_failed_test_uids(driver: webdriver) -> list:
    """Gets UIDs of failed tests."""
    response = driver.page_source
    tree = html.fromstring(response)
    test_xpath = "(//*[@data-tooltip='Broken'] | //*[@data-tooltip='Failed'] )/../../../@href"
    tests = tree.xpath(test_xpath)
    test_uids = list(map(lambda x: x.split("/")[2], tests))
    return test_uids

def scrape_uid_list_data(uids: list, base_url: str) -> dict:
    """Iterate through uid list."""
    data = {}
    for uid in uids:
        logger.debug(f"Scraping UID: {uid}")
        response_data = scrape_uid(uid, base_url)
        data[uid] = response_data
        random_wait(2)
    logger.debug("Scraping UIDs complete")
    return data

def scrape_uid(uid: str, base_url: str):
    headers = set_headers()
    data_url = f"{base_url}data/test-cases/{uid}.json"
    response = requests.get(data_url, headers=headers)
    response_data = response.json()
    return response_data

def random_wait(base_wait: int) -> None:
    """Waits a random period"""
    rand_num = base_wait + random.randint(0,3)
    time.sleep(rand_num)

def save_scrape_data_to_json(date: str, data: dict) -> None:
    """Saves data to json file"""
    date = date.replace("/", "-")
    with open(f"test_run_{date}.json", "w") as file:
        json.dump(data, file)

def update_base_url(driver: webdriver) -> str:
    """Updates the base url"""
    return driver.current_url

def get_test_data_url_list(page_source: str) -> list:
    """Gets test data url list"""



def driver_setup():
    # chromeOptions = webdriver.ChromeOptions()
    # chromeOptions.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    # chromeOptions.add_argument("--no-sandbox")
    # chromeOptions.add_argument("--disable-setuid-sandbox")
    # chromeOptions.add_argument("--remote-debugging-port=9222") # this
    # chromeOptions.add_argument("--disable-dev-shm-using")
    # chromeOptions.add_argument("--disable-extensions")
    # chromeOptions.add_argument("--disable-gpu")
    # chromeOptions.add_argument("start-maximized")
    # chromeOptions.add_argument("disable-infobars")
    # chromeOptions.add_argument(r"user-data-dir=.\cookies\\test")
    # b = webdriver.Chrome(chrome_options=chromeOptions)
    b = webdriver.Chrome()
    return b

