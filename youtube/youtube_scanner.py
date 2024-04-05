from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)

from bs4 import BeautifulSoup

import time

baseURL = "https://www.youtube.com"

#Youtube Information Schema
class youtubeChannelInfo:
    def __init__(self):
        self.name = None
        self.subCount = None
        self.VidCount = None

class youtubeScanner:
    def __init__(self, target):
        self.target = target

        self.data = youtubeChannelInfo()

        #start Selenium in headless mode
        options = Options()
        options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)

    def getFullURL(self):
        if self.target.find(baseURL) == -1:
            return f"{baseURL}/@{self.target}"
        else:
            return self.target

    def open(self):
        fullURL = self.getFullURL()
        self.driver.get(fullURL)

        time.sleep(5)

        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        with open("output/temp.txt", "w") as f:
            f.write(soup.prettify())

        self.driver.close()