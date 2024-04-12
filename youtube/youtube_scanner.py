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
from selenium.webdriver.common.action_chains import ActionChains

from bs4 import BeautifulSoup

import time
import os
from datetime import date
import math

from youtube.exceptions import ParseFailedException
from helpers.counter import Counter

baseURL = "https://www.youtube.com"

#YouTube Identifiers
aboutContainerID = "about-container"

#YouTube Information Schema
class youtubeVideoInfo:
    def __init__(self, title=None, date=None, views=None, likes=None, commentCount=None, URL=None):
        self.title = title
        self.date = date
        self.views = views
        self.likes = likes
        self.commentCount = commentCount
        self.URL = URL

class youtubeChannelInfo:
    def __init__(self):
        self.title = None
        self.about = None
        self.subCount = None
        self.vidCount = None
        self.viewCount = None
        self.joinDate = None
        self.socmedLinks = []
        self.videos = []
        self.shorts = []
        self.livestreams = []

class youtubeScanner:
    def __init__(self, target):
        self.target = target

        self.data = youtubeChannelInfo()

        self.videosFound = False
        self.shortsFound = False
        self.liveFound = False

        self.aboutSoup = None
        self.videoSoup = None
        self.shortsSoup = None
        self.liveSoup = None

        #start Selenium in headless mode
        options = Options()
        options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)

    def getFullURL(self):
        if self.target.find(baseURL) == -1:
            return f"{baseURL}/@{self.target}"
        else:
            return self.target
        
    def __openPage(self, pageName):
        self.driver.get(self.getFullURL() + pageName)

        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "style-scope.ytd-rich-grid-renderer"))
            )

            chips = self.driver.find_elements(By.TAG_NAME, "yt-chip-cloud-chip-renderer")

            #print(len(chips))
            if len(chips) > 0:
                page = self.driver.find_element(By.TAG_NAME, "body")

                chips[2].click() #click oldest chip
                time.sleep(1)

                #get oldest video title
                oldestTitle = self.driver.find_element(By.ID, "video-title").text

                chips[0].click() #click newest chip
                time.sleep(1)

                titles = []

                #scroll down until the oldest video title is found
                while True:
                    titles = self.driver.find_elements(By.ID, "video-title")
                    lastTitle = titles[len(titles)-1].text
                    #print(lastTitle)
                    if lastTitle == oldestTitle:
                        break
                    page.send_keys(Keys.END)
                    time.sleep(1)

                for title in titles:
                    print(title.text)

            if pageName == "/videos":
                self.videoSoup = BeautifulSoup(self.driver.page_source, "html.parser")
            elif pageName == "/shorts":
                self.shortsSoup = BeautifulSoup(self.driver.page_source, "html.parser")
            elif pageName == "/streams":
                self.liveSoup = BeautifulSoup(self.driver.page_source, "html.parser")

            print(f"{pageName} Opened.")
        except TimeoutException:
            print(f"{pageName} Open Failed: Empty Page. Proceeding...")
            if pageName == "/videos":
                self.videosFound == False
            elif pageName == "/shorts":
                self.shortsFound == False
            elif pageName == "/streams":
                self.liveFound == False


    def open(self):
        fullURL = self.getFullURL()
        print(f"Opening {fullURL}...")

        self.driver.get(fullURL)

        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "yt-tab-group-shape-wiz__tabs"))
        )

        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        self.videosFound = soup.find(attrs={"tab-title": "Videos"}) is not None
        self.shortsFound = soup.find(attrs={"tab-title": "Shorts"}) is not None
        self.liveFound = soup.find(attrs={"tab-title": "Live"}) is not None

        print(f"Video Page Found: {self.videosFound}")
        print(f"Shorts Page Found: {self.shortsFound}")
        print(f"Live Page Found: {self.liveFound}")

        self.driver.get(fullURL + "/about")

        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, aboutContainerID))
            )
        except TimeoutException:
            raise ParseFailedException("Parse Failed: cannot read About page.")
        
        self.aboutSoup = BeautifulSoup(self.driver.page_source, "html.parser")

        if self.videosFound:
            self.__openPage("/videos")
        if self.shortsFound:
            self.__openPage("/shorts")
        if self.liveFound:
            self.__openPage("/streams")

        print("Open Done.")

    def __scanVideo(self, vidURL):
        self.driver.get(vidURL)

        titleXPath = '//*[@id="title"]/h1/yt-formatted-string'
        commentsXPath = '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-comments/ytd-item-section-renderer/div[1]/ytd-comments-header-renderer/div[1]/div[1]/h2/yt-formatted-string'

        WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, titleXPath))
            )

        expandButton = self.driver.find_element(By.ID, "expand")
        expandButton.click()
        time.sleep(1)

        vidTitle = self.driver.find_element(By.XPATH, titleXPath).text
        print(vidTitle)

        watchInfoString = self.driver.find_element(By.CLASS_NAME, "style-scope.ytd-watch-info-text").text.strip()
        watchInfoList = watchInfoString.split("  ")

        #print(watchInfoList)

        vidDate = watchInfoList[1].replace("Premiered ", "")
        vidViews = watchInfoList[0].replace(" views", "")

        """collapseButton = self.driver.find_element(By.ID, "collapse")
        collapseButton.click()
        time.sleep(1)

        page = self.driver.find_element(By.TAG_NAME, "body")
        page.send_keys(Keys.END)
        time.sleep(5)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        page = self.driver.find_element(By.TAG_NAME, "body")
        page.send_keys(Keys.END)
        page.send_keys(Keys.PAGE_DOWN)
        time.sleep(1)

        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, commentsXPath))
            )
        except TimeoutException:
            timeoutSoup = BeautifulSoup(self.driver.page_source, "html.parser")
            with open("output/temp.html", "w") as f:
                f.write(timeoutSoup.prettify())
            self.driver.save_screenshot("output/page.png")
            raise ParseFailedException("Parse Failed: Timeout while waiting for comments to load") """

        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        likeButton = soup.find("like-button-view-model")
        vidLikes = likeButton.find(class_="yt-spec-button-shape-next__button-text-content").text

        """ comments = soup.find("ytd-comments", id="comments")
        vidCommentCount = comments.find(id="leading-section").text.strip().replace(" Comments", "") """

        return youtubeVideoInfo(title=vidTitle, date=vidDate, views=vidViews, likes=vidLikes, URL=vidURL)

    def __scanVideos(self):
        videos = self.videoSoup.find(id="contents", class_="style-scope ytd-rich-grid-renderer")
        videoLinks = videos.find_all("a", id="video-title-link")

        counter = Counter(len(videoLinks))
        for link in videoLinks[:3]: #reminder to remove list slice after implementing shorts and livestream scrapping
            counter.inc()
            fullLink = baseURL + link["href"]
            print(f"{counter} Scanning {fullLink}...", end=" ")
            self.data.videos.append(self.__scanVideo(fullLink))

    def scan(self):
        print("Initiating Scan...")
        
        #Channel Details
        self.data.title = self.aboutSoup.find("yt-formatted-string", class_="style-scope ytd-channel-name").text
        self.data.about = self.aboutSoup.find(id="description-container").text.strip()

        details = self.aboutSoup.find(id="additional-info-container")
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
        linkContainer = self.aboutSoup.find(id="link-list-container")
        links = linkContainer.find_all("yt-channel-external-link-view-model")

        for link in links:
            linkParts = link.find_all("span")
            self.data.socmedLinks.append((linkParts[0].text, linkParts[1].text))

        #Video Pages
        if self.videosFound:
            self.__scanVideos()
        
        print("Scan Done.")
            

    def display(self):
        #General Channel Info
        print(f"Channel Title: {self.data.title}")
        print(f"About: {self.data.about}\n")
        print(f"Subscribers: {self.data.subCount}")
        print(f"Videos: {len(self.data.videos)}/{self.data.vidCount}")
        print(f"Views: {self.data.viewCount}")
        print(f"Join Date: {self.data.joinDate}\n")

        if len(self.data.socmedLinks) > 0:
            print("Other Links:")
            for link in self.data.socmedLinks:
                print(f" {link[0]} - {link[1]}")
        else:
            print("No External Links Detected.")

        #Videos
        """ print("\n===VIDEOS===")
        for vid in self.data.videos:
            print(f"Title: {vid.title}")
            print(f"Date: {vid.date}")
            print(f"Views: {vid.views}")
            print(f"Likes: {vid.likes}")
            #print(f"Comments: {vid.commentCount}")
            print(vid.URL)
            print() """
        
        #Shorts

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

            f.write("VIDEOS\n")
            f.write("Video,Title,Date,Views,Likes,URL\n")
            counter = 1
            for vid in self.data.videos:
                sanitizedTitle = vid.title.replace('\"', '\"\"')
                f.write(f"{counter},\"{sanitizedTitle}\",\"{vid.date}\",\"{vid.views}\",\"{vid.likes}\",{vid.URL}\n")
                counter += 1

    def close(self):
        self.driver.close()