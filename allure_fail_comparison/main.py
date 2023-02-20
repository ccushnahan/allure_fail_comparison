"""Main module for allure fail comparison."""
import os
import pickle
import subprocess
import time
import urllib

from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from allure_scraper import scrape_allure_report
from allure_data import process_data, export_data


def main():
    """Main method"""
    # get sysarg

    # pass to allure method
    report_url = "https://allure-examples.github.io/allure-cucumber5-testng-gradle/"
    data, date, url = scrape_allure_report(report_url)
    df = process_data(data, url)
    export_data(df, date)

if __name__ == "__main__":
    main()