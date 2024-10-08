from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By

from cleantext import clean

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
        self.__scanAbout()

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
                print("Livestream Detected.")

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

    def __scanAbout(self):
        print("Scanning About Page...")

        self.driver.get(self.getFullURL() + "/about")

        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "offline-channel-main-content"))
            )

            time.sleep(1)

            about = self.driver.find_element(By.ID, "offline-channel-main-content")
            basicAbout = about.find_element(By.XPATH, "div[3]/div/div/div/div[1]/div[2]/div/div/div[2]/div")
            panels = about.find_element(By.XPATH, "div[3]/div/div/div/div[2]")

            # since not every streamer has a team, this method is used to detect if there's a team
            # named in the streamer's about page. This method assumes that the team name always appears
            # last in the string
            aboutStatString = basicAbout.find_element(By.XPATH, "div[1]/div")
            aboutStatList = aboutStatString.text.split("\n")
            team = None
            if len(aboutStatList) >= 4:
                team = aboutStatList[3]

            description = basicAbout.find_element(By.XPATH, "div[1]/p")

            linkList = []
            try:
                linkContainer = basicAbout.find_element(By.XPATH, "div[2]/div/div/div")
                links = linkContainer.find_elements(By.XPATH, "div")
                
                for link in links:
                    anchor = link.find_element(By.XPATH, "div[1]/div/a")
                    href = anchor.get_attribute("href")
                    #print(f"link: {anchor.text} - {href}")
                    cleanLinkName = clean(link.text, no_emoji=True, lower=False)
                    linkList.append((cleanLinkName, href))
            except NoSuchElementException:
                print("No External Links Detected. Proceeding...")

            self.info.team = team
            self.info.description = description.text
            self.info.externalLinks = linkList

        except TimeoutException:
            print("ERROR")

    """ def record(self):
        print("RECORDING DISABLED.") """