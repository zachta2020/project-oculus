"""
Common interface for website scanner objects
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FireFoxOptions

import os

from common.info import Info

class Scanner:
    def __init__(self, target: str, website: str, info: Info, driverSelect: str = "chrome"):
        self.target: str = target
        self.website: str = website
        self.info: Info = info

        if driverSelect.lower() == "chrome":
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--headless=new")
            self.driver = webdriver.Chrome(options=chrome_options)
        elif driverSelect.lower() == "firefox":
            firefox_options = FireFoxOptions()
            firefox_options.add_argument("-headless")
            self.driver = webdriver.Firefox(options=firefox_options)

    def getFullURL(self):
        pass

    def run(self):
        pass

    def display(self):
        print(self.info)

    def record(self):
        output = "output"
        if not os.path.exists(output):
            os.makedirs(output)

        fileName = f"{output}/{self.target}_{self.website}_results_{self.info.get_date()}.csv"
        print(f"Saving to {fileName}...")

        with open(fileName, "w", encoding="utf8") as f:
            f.write(self.info.csv())

        print("Record Done.")

    def close(self):
        self.driver.close()