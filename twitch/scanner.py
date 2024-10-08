from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By

from common.scanner import Scanner
from twitch.info import TwitchInfo, TwitchStream

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

            try: #assuming the streamer is offline
                basicInfo = self.driver.find_element(By.ID, "offline-channel-main-content")

                title = basicInfo.find_element(By.XPATH, "//h1")
                followers = basicInfo.find_element(By.XPATH, "div[2]/div[1]/div[1]/div[2]/p")

                #print(f"{title.text}\n{followers.text}")

                self.info.title = title.text
                self.info.followerCount = followers.text.replace(" followers", "")
            except NoSuchElementException: #if the streamer is live
                basicInfo = self.driver.find_element(By.ID, "live-channel-about-panel")
                aboutPanel = basicInfo.find_element(By.XPATH, "div[1]/div[2]/div[1]/div[1]")

                title = aboutPanel.find_element(By.XPATH, "div[1]/div[1]/h3")
                followers = aboutPanel.find_element(By.XPATH, "div[2]/div/div/div/div/div/span/div/div/span")

                #print(followers.text)

                self.info.title = title.text.replace("About ", "")
                self.info.followerCount = followers.text

                #scan current stream since the streamer is live
                stream = self.driver.find_element(By.ID, "live-channel-stream-information")
                streamInfo = stream.find_element(By.XPATH, "div/div/div[2]/div/div[2]/div[2]")

                streamTitle = streamInfo.find_element(By.XPATH, "div[1]/div/div[1]")
                streamGame = streamInfo.find_element(By.XPATH, "div[1]/div/div[2]/div/div/div[1]")
                streamTags = streamInfo.find_element(By.XPATH, "div[1]/div/div[2]/div/div/div[2]")

                streamViewers = streamInfo.find_element(By.XPATH, "div[2]/div/div/div[1]/div[1]")
                streamRuntime = streamInfo.find_element(By.XPATH, "div[2]/div/div/div[1]/div[2]")

                taglist = streamTags.text.split("\n")
                viewerCount = int(streamViewers.text.replace(",", ""))

                self.info.currentStream = TwitchStream(title=streamTitle.text, game=streamGame.text, tags=taglist, viewerCount=viewerCount, currentRuntime=streamRuntime.text)

        except TimeoutException:
            print("ERROR")

    def record(self):
        print("RECORDING DISABLED.")