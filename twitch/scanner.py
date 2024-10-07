from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By

from common.scanner import Scanner
from twitch.info import TwitchInfo

import time

baseURL = "https://www.twitch.tv"

class TwitchScanner(Scanner):
    def __init__(self, target):
        super().__init__(target, "twitch", TwitchInfo())

    def getFullURL(self):
        if self.target.find(baseURL) == -1:
            return f"{baseURL}/{self.target}"
        else:
            return self.target
        
    def run(self):
        self.__scanHome()

    def __scanHome(self):
        fullURL = self.getFullURL()
        print(f"Scanning {fullURL}...")

        self.driver.get(fullURL)

        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "channel-info-content"))
            )

            time.sleep(1) #to ensure that followers text loads

            #self.driver.save_screenshot("secret/twitch.png")

            basicInfo = self.driver.find_element(By.ID, "offline-channel-main-content")

            title = basicInfo.find_element(By.XPATH, "//h1")
            followers = basicInfo.find_element(By.XPATH, "div[2]/div[1]/div[1]/div[2]/p")

            #print(f"{title.text}\n{followers.text}")

            self.info.title = title.text
            self.info.followerCount = followers.text.replace(" followers", "")







        except TimeoutException:
            print("ERROR")

    def record(self):
        print("RECORDING DISABLED.")