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
import os
from datetime import date

from youtube.exceptions import ParseFailedException

baseURL = "https://www.youtube.com"

#YouTube Identifiers
aboutContainerID = "about-container"

#YouTube Information Schema
class youtubeChannelInfo:
    def __init__(self):
        self.title = None
        self.about = None
        self.subCount = None
        self.vidCount = None
        self.viewCount = None
        self.joinDate = None
        self.socmedLinks = []

class youtubeScanner:
    def __init__(self, target):
        self.target = target

        self.data = youtubeChannelInfo()

        #start Selenium in headless mode
        options = Options()
        options.add_argument("--headless=new")
        self.aboutDriver = webdriver.Chrome(options=options)
        #self.videoDriver = webdriver.Chrome(options=options)

    def getFullURL(self):
        if self.target.find(baseURL) == -1:
            return f"{baseURL}/@{self.target}"
        else:
            return self.target

    def open(self):
        fullURL = self.getFullURL()
        print(f"Opening {fullURL}...")

        self.aboutDriver.get(fullURL + "/about")
        #self.videoDriver.get(fullURL + "/videos")

        try:
            WebDriverWait(self.aboutDriver, 5).until(
                EC.presence_of_element_located((By.ID, aboutContainerID))
            )
        except TimeoutException:
            raise ParseFailedException("Parse Failed: cannot read About page.")

        print("Open Done.")


    def scan(self):
        print("Initiating Scan...")
        aboutSoup = BeautifulSoup(self.aboutDriver.page_source, "html.parser")

        #Channel Details
        self.data.title = aboutSoup.find("yt-formatted-string", class_="style-scope ytd-channel-name").text
        self.data.about = aboutSoup.find(id="description-container").text.strip()

        details = aboutSoup.find(id="additional-info-container")
        detailsList = details.text.split("\n")
        for e in detailsList:
            if e.find("subscriber") != -1:
                self.data.subCount = e.split(" ").pop(0)
            elif e.find("video") != -1:
                self.data.vidCount = e.split(" ").pop(0)
            elif e.find("view") != -1:
                self.data.viewCount = e.split(" ").pop(0)
            elif e.find("Joined ") != -1:
                self.data.joinDate = e.replace("Joined ", "")

        #External Social Media Links
        linkContainer = aboutSoup.find(id="link-list-container")
        links = linkContainer.find_all("yt-channel-external-link-view-model")

        for link in links:
            linkParts = link.find_all("span")
            self.data.socmedLinks.append((linkParts[0].text, linkParts[1].text))
        
        print("Scan Done.")
            

    def display(self):
        print(f"Channel Title: {self.data.title}")
        print(f"About: {self.data.about}\n")
        print(f"Subscribers: {self.data.subCount}")
        print(f"Videos: {self.data.vidCount}")
        print(f"Views: {self.data.viewCount}")
        print(f"Join Date: {self.data.joinDate}\n")

        if len(self.data.socmedLinks) > 0:
            print("Other Links:")
            for link in self.data.socmedLinks:
                print(f" {link[0]} - {link[1]}")
        else:
            print("No External Links Detected.")

    def record(self):
        output = "output"
        if not os.path.exists(output):
            os.makedirs(output)    

        fileName = f"{output}/{self.getFullURL().split('@').pop()}_youtube_results_{date.today()}.csv"
        print(f"Saving Results to {fileName}...")

        with open(fileName, "w", encoding="utf8") as f:
            f.write(f"YouTube Channel,{self.data.title}\n")
            sanitizedAbout = self.data.about.replace('\"', '\"\"')
            f.write(f"About,\"{sanitizedAbout}\"\n")
            f.write(f"Subscribers,\"{self.data.subCount}\"\n")
            f.write(f"Videos,\"{self.data.vidCount}\"\n")
            f.write(f"Views,\"{self.data.viewCount}\"\n")
            f.write(f"Join Date,\"{self.data.joinDate}\"\n")

            if len(self.data.socmedLinks) > 0:
                f.write("External,Website,Link\n")
                for link in self.data.socmedLinks:
                    f.write(f",{link[0]},{link[1]}\n")
            else:
                f.write("No External Links Detected\n")