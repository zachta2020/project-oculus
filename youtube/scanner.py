from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FireFoxOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
)

from bs4 import BeautifulSoup

import time

from common.exceptions import ParseFailedException
from common.scanner import Scanner
from common.helpers.counter import Counter
from youtube.helpers.date_util import relative_to_absolute
from youtube.info import *

baseURL = "https://www.youtube.com"

#YouTube Identifiers
aboutContainerID = "about-container"

#Youtube Scanning Object
class youtubeScanner(Scanner):
    def __init__(self, target):
        super().__init__(target, "youtube", YouTubeChannelInfo(), "firefox")

        self.videosFound: bool = False
        self.shortsFound: bool = False
        self.liveFound: bool = False

        self.aboutSoup = None
        self.videoSoup = None
        self.shortsSoup = None
        self.liveSoup = None

        #temp until youtube video scanner is factored out
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless=new")
        self.videoDriver = webdriver.Chrome(options=chrome_options)

    def getFullURL(self):
        if self.target.find(baseURL) == -1:
            return f"{baseURL}/@{self.target}"
        else:
            return self.target
        
    def run(self):
        self.__open()
        print()
        self.__scan()
        
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
                oldestTitle = ""
                if pageName == "/shorts":
                    oldestTitle = self.driver.find_element(By.CLASS_NAME, "ShortsLockupViewModelHostEndpoint.ShortsLockupViewModelHostOutsideMetadataEndpoint").text
                else:
                    oldestTitle = self.driver.find_element(By.ID, "video-title").text

                chips[0].click() #click newest chip
                time.sleep(1)

                titles = []

                #scroll down until the oldest video title is found
                counter = 1
                while True:
                    titles = []
                    if pageName == "/shorts":
                        titles = self.driver.find_elements(By.CLASS_NAME, "ShortsLockupViewModelHostEndpoint.ShortsLockupViewModelHostOutsideMetadataEndpoint")
                    else:
                        titles = self.driver.find_elements(By.ID, "video-title")
                    lastTitle = titles[len(titles)-1].text
                    if lastTitle == oldestTitle:
                        break
                    print(f"Scroll {counter}...")
                    counter += 1
                    page.send_keys(Keys.END)
                    time.sleep(2)

                
            """ titles = self.driver.find_elements(By.ID, "video-title")
            for title in titles[:5]:
                    print(title.text) """
            

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
                self.videosFound = False
            elif pageName == "/shorts":
                self.shortsFound = False
            elif pageName == "/streams":
                self.liveFound = False

    def __open(self):
        fullURL = self.getFullURL()
        print(f"Opening {fullURL}...")

        self.driver.get(fullURL)

        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "yt-tab-group-shape-wiz__tabs"))
            )
        except TimeoutException:
            raise ParseFailedException("Parse Failed: User does not exist.")

        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        self.videosFound = soup.find(attrs={"tab-title": "Videos"}) is not None
        self.shortsFound = soup.find(attrs={"tab-title": "Shorts"}) is not None
        self.liveFound = soup.find(attrs={"tab-title": "Live"}) is not None

        print(f"Video Page Found: {self.videosFound}")
        print(f"Shorts Page Found: {self.shortsFound}")
        print(f"Live Page Found: {self.liveFound}")

        #self.info.title = self.openDriver.find_element(By.CLASS_NAME, "yt-core-attributed-string.yt-core-attributed-string--white-space-pre-wrap")

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
        self.videoDriver.get(vidURL)

        titleXPath = '//*[@id="title"]/h1/yt-formatted-string'

        WebDriverWait(self.videoDriver, 10).until(
                EC.presence_of_element_located((By.XPATH, titleXPath))
            )

        vidTitle = self.videoDriver.find_element(By.XPATH, titleXPath).text
        print(vidTitle)

        #print(watchInfoList)

        soup = BeautifulSoup(self.videoDriver.page_source, "html.parser")

        #Test of improvement
        watchInfoTestString = soup.find("tp-yt-paper-tooltip", class_="style-scope ytd-watch-info-text").text.strip()
        watchInfoList = watchInfoTestString.split(" • ")
        """ for e in watchInfoList:
            print(e) """

        likeButton = soup.find("like-button-view-model")

        vidLikes = ""
        try:
            vidLikes = likeButton.find(title="I like this")["aria-label"].split(" ")[5]
        except IndexError:
            print("Like count not found. Proceeding...")
            vidLikes = "Hidden"

        if watchInfoList[1].find("Premieres") != -1 or watchInfoList[1].find("Scheduled") != -1: #pre scheduled
            vidDate = watchInfoList[1].replace("Premieres ", "").replace("Scheduled for ", "")
            vidWaiting = watchInfoList[0].replace(" waiting", "")
            return youtubeScheduledInfo(title=vidTitle, date=vidDate, waiting=vidWaiting, likes=vidLikes, URL=vidURL)
        elif watchInfoList[1].find("Premiere in progress") != -1 or watchInfoList[1].find("Started") != -1: #in progress
            vidCurrentViewers = watchInfoList[0].replace(" watching now", "")
            vidDate = watchInfoList[1].replace("Premiere in progress. Started ", "").replace("Started streaming ", "")
            if vidDate.find("ago") != -1:
                vidDate = relative_to_absolute(vidDate)
            else:
                vidDate = vidDate.replace("on ", "")
            return youtubeCurrentInfo(title=vidTitle, date=vidDate, currentViewers=vidCurrentViewers, likes=vidLikes, URL=vidURL)
        else: #done
            vidDate = watchInfoList[1].replace("Premiered ", "").replace("Streamed live ", "")
            vidViews = watchInfoList[0].replace(" views", "")
            if vidDate.find("ago") != -1:
                vidDate = relative_to_absolute(vidDate)
            else:
                vidDate = vidDate.replace("on ", "")
            return youtubeVideoInfo(title=vidTitle, date=vidDate, views=vidViews, likes=vidLikes, URL=vidURL)
    
    def __scanShort(self, shortURL):
        self.videoDriver.get(shortURL)

        titleClassName = "title.style-scope.reel-player-header-renderer"

        #self.driver.save_screenshot("output/page.png")
        
        shortTitle = self.videoDriver.find_element(By.CLASS_NAME, titleClassName).text

        print(shortTitle)

        soup = BeautifulSoup(self.videoDriver.page_source, "html.parser")
        """ with open("output/shortsPage.html", "w") as f:
            f.write(soup.prettify()) """
        
        factoids = soup.find_all(class_="YtwFactoidRendererHost")

        #print(len(factoids))

        #the factoids are stored in the order of Likes, Views, and then Date in the list

        shortInfo = []
        for fact in factoids:
            firstHalf = fact.find(class_="YtwFactoidRendererValue").text
            secondHalf = fact.find(class_="YtwFactoidRendererLabel").text
            shortInfo.append((firstHalf, secondHalf))

            """ print("===")
            print(f"{firstHalf} {secondHalf}")
            print("===") """

        shortDate = f"{shortInfo[2][0]}, {shortInfo[2][1]}"
        shortViews = shortInfo[1][0]
        shortLikes = shortInfo[0][0]

        return youtubeVideoInfo(title=shortTitle, date=shortDate, views=shortViews, likes=shortLikes, URL=shortURL)

    def __scanPage(self, pageName):
        if pageName == "videos":
            videos = self.videoSoup.find(id="contents", class_="style-scope ytd-rich-grid-renderer")
        elif pageName == "shorts":
            videos = self.shortsSoup.find(id="contents", class_="style-scope ytd-rich-grid-renderer")
        elif pageName == "streams":
            videos = self.liveSoup.find(id="contents", class_="style-scope ytd-rich-grid-renderer")

        videoLinks = []
        if pageName == "shorts":
            videoLinks = videos.find_all("a", class_="ShortsLockupViewModelHostEndpoint reel-item-endpoint")
        else:
            videoLinks = videos.find_all("a", id="video-title-link")
        
        print(f"Total Found: {len(videoLinks)}")
        counter = Counter(len(videoLinks))
        for link in videoLinks:
            counter.inc()
            fullLink = baseURL + link["href"]
            retryAttempts = 5
            
            while True:
                print(f"{counter} Scanning {fullLink}...", end=" ")
                try:
                    if pageName == "videos":
                        videoInfo = self.__scanVideo(fullLink)
                        if videoInfo.__class__.__name__ == "youtubeVideoInfo":
                            self.info.videos.append(videoInfo)
                        elif videoInfo.__class__.__name__ == "youtubeCurrentInfo":
                            self.info.premieringVideos.append(videoInfo)
                        elif videoInfo.__class__.__name__ == "youtubeScheduledInfo":
                            self.info.scheduledVideos.append(videoInfo)
                    elif pageName == "shorts":
                        self.info.shorts.append(self.__scanShort(fullLink))
                    elif pageName == "streams":
                        streamInfo = self.__scanVideo(fullLink)
                        if streamInfo.__class__.__name__ == "youtubeVideoInfo":
                            self.info.livestreamVODs.append(streamInfo)
                        elif streamInfo.__class__.__name__ == "youtubeCurrentInfo":
                            self.info.currentLivestreams.append(streamInfo)
                        elif streamInfo.__class__.__name__ == "youtubeScheduledInfo":
                            self.info.scheduledLivestreams.append(streamInfo)
                    break
                except NoSuchElementException as e:
                    if retryAttempts > 0:
                        print("SCAN FAILED: UNABLE TO FIND ELEMENT. Retrying...")
                        retryAttempts -= 1
                        continue
                except TimeoutException:
                    if retryAttempts > 0:
                        print("SCAN FAILED: TIMEOUT. Retrying...")
                        retryAttempts -= 1
                        continue

                if retryAttempts == 0:
                    print("CANNOT SCAN VIDEO. Proceeding...")
                    if pageName == "videos":
                        self.info.videos.append(youtubeVideoInfo(title="UNKNOWN", URL=fullLink))
                    elif pageName == "shorts":
                        self.info.shorts.append(youtubeVideoInfo(title="UNKNOWN", URL=fullLink))
                    elif pageName == "streams":
                        self.info.livestreams.append(youtubeVideoInfo(title="UNKNOWN", URL=fullLink))
                    break

    def __scan(self):
        print("Initiating Scan...")
        
        #Channel Details
        self.info.title = self.aboutSoup.find("span", class_="yt-core-attributed-string yt-core-attributed-string--white-space-pre-wrap").text
        self.info.about = self.aboutSoup.find(id="description-container").text.strip()

        details = self.aboutSoup.find(id="additional-info-container")
        detailsList = details.text.split("\n")
        for e in detailsList:
            if e.find("subscriber") != -1:
                self.info.subCount = e.split(" ").pop(0)
            elif e.find("video") != -1:
                self.info.vidCount = e.split(" ").pop(0)
            elif e.find("view") != -1:
                self.info.viewCount = e.split(" ").pop(0)
            elif e.find("Joined ") != -1:
                self.info.joinDate = e.replace("Joined ", "")

        #External Social Media Links
        linkContainer = self.aboutSoup.find(id="link-list-container")
        links = linkContainer.find_all("yt-channel-external-link-view-model")

        for link in links:
            linkParts = link.find_all("span")
            self.info.socmedLinks.append((linkParts[0].text, linkParts[1].text))

        #Video Pages
        if self.videosFound:
            print("Scanning Videos...")
            self.__scanPage("videos")
        if self.shortsFound:
            print("Scanning Shorts...")
            self.__scanPage("shorts")
        if self.liveFound:
            print("Scanning Livestreams...")
            self.__scanPage("streams")
        
        print("Scan Done.")

    def close(self):
        super().close()
        self.videoDriver.close()