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
import math

from common.scanner import Scanner
from common.exceptions import ParseFailedException
from patreon.info import PatreonInfo, PatreonPost

#patreon identifiers
#titleClass = "sc-cNKqjZ.ldIKdq"
#subtitleClass = "sc-dkPtRN.cUqLgq"
memberCountXPath = "//span[@data-tag='patron-count']"
postCountXPath = "//span[@data-tag='creation-count']"
incomeXPath = "//span[@data-tag='earnings-count']"

seeMoreXPath = "//div[@data-tag='creator-public-page-recent-posts']/div[4]/button"
ageConfirmXPath = "//button[@data-tag='age-confirmation-button']"
postListXPath = "//div[@data-tag='creator-public-page-recent-posts']"

baseURL = "https://www.patreon.com"

class patreonScanner(Scanner):
    def __init__(self, target):
        super().__init__(target, "patreon", PatreonInfo())

    def getFullURL(self):
        if self.target.find(baseURL) == -1:
            return f"{baseURL}/{self.target}"
        else:
            return self.target
        
    def run(self):
        self.__open()
        print()
        self.__scan()

    def __open(self):
        fullURL = self.getFullURL()
        print(f"Opening {fullURL}...\n")
        self.driver.get(fullURL)
    
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, postListXPath))
        )
        except TimeoutException:
            print("A timeout has occured. Attempting Age Confirmation Check...")
            try:
                ageConfirm = self.driver.find_element(By.XPATH, ageConfirmXPath)
                ageConfirm.click()
                print("Success! Proceeding.\n")
            except NoSuchElementException:
                print("Age Confirmation Check failed.")
                raise ParseFailedException("Parse Failed: Cannot read Creator page.")
            
        try: #Does the age confirm not timeout the postlist check anymore?
            ageConfirm = self.driver.find_element(By.XPATH, ageConfirmXPath)
            ageConfirm.click()
        except NoSuchElementException:
            pass
            
        # display all posts
        postTotal = float(
                self.driver.find_element(By.XPATH, postCountXPath)
                .text.split(" ")[0]
                .replace(",", "")
            )

        postInc = 20.0
        
        if postTotal > postInc: 
            print("Displaying all posts...")

            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, seeMoreXPath))
                )

                """ buttons = self.driver.find_elements(By.XPATH, "//div[@data-tag='creator-public-page-recent-posts']/div[4]/button")
                print(f"DEBUG: {len(buttons)}")
                counter = 1
                for button in buttons:
                    print(f"{counter} - {button.text}")
                    counter += 1 """

                
                clickEstimate = int(math.ceil((postTotal - postInc) / postInc))
                clickCounter = 1

                seeMore = self.driver.find_element(By.XPATH, seeMoreXPath)
                page = self.driver.find_element(By.TAG_NAME, "body")

                seeMore.click()
                print(f"Click {clickCounter}/{clickEstimate}")
                clickCounter += 1

                while True:
                    try:
                        time.sleep(1)
                        page.send_keys(Keys.END)
                        time.sleep(1)
                        seeMore.click()
                        print(f"Click {clickCounter}/{clickEstimate}")
                        clickCounter += 1
                    except ElementClickInterceptedException:
                        print("Error: Click Intercepted. Retrying...")
                    except StaleElementReferenceException:
                        print("End of Page found. Proceeding...")
                        break

            except NoSuchElementException:
                print("Error: Cannot find button")
                raise ParseFailedException("Parse Failed: Cannot read Creator page.")

        print("Open Done.")

    def __scan(self):
        print("Initiating Scan...")

        titleList = self.driver.title.split("|")
        
        self.info.title = titleList[0]
        self.info.subtitle = titleList[1].strip()

        try:
            self.info.memberCount = int(
                self.driver.find_element(By.XPATH, memberCountXPath).text.split(" ")[0].replace(",", "")
            )
        except NoSuchElementException:
            pass

        self.info.postCount = int(
            self.driver.find_element(By.XPATH, postCountXPath).text.split(" ")[0].replace(",", "")
        )

        try:
            self.info.income = self.driver.find_element(By.XPATH, incomeXPath).text
        except NoSuchElementException:
            pass

        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        with open("output/patreon_broke.html", "w") as f:
            f.write(self.driver.page_source)

        recentPosts = soup.find(attrs={"data-tag": "all-posts-layout"})
        postList = recentPosts.find_all(attrs={"data-tag": "post-card"})

        for post in postList:

            postTitle = post.find(attrs={"data-tag": "post-title"})
            postTitleText = "Title Not Found."

            """ if postTitle is not None:
                print(f"DEBUG: Reading {postTitle.text}")
            else:
                print(f"DEBUG: Reading {postTitleText}") """
            
            #self.driver.save_screenshot("secret/postDebug.png")

            if postTitle != None:
                postTitleText = postTitle.text

            #Post Date
            postDate = post.find(attrs={"data-tag": "post-published-at"})
            postDateText = "N/A"
            if postDate is None:
                postDateText = post.find(id="track-click").text
            else:
                postDateText = postDate.text

            #Post Link
            postTitleAnchor = None
            if postTitle is not None:
                postTitleAnchor = postTitle.find("a")

            postLink = "N/A"
            if postTitleAnchor is not None: #when the post is not locked and has a title
                postLink = postTitleAnchor["href"]
            elif postDate is not None: #if the post is not locked but has no title
                postLink = postDate["href"]
            else: #if the post is locked
                try:
                    postLockedLink = post.find("a", attrs={"data-tag":"join-button"})["href"]
                    #scrubbing the link
                    postLink = postLockedLink.replace("login?ru=%2F", "")
                    postLink = postLink.replace("%2F", "/")
                    postLink = postLink.replace("%3Fimmediate_pledge_flow%3Dtrue", "")
                except TypeError:
                    postLink = post.find("a", attrs={"data-tag":"comment-post-icon"})["href"]

            #Post Locked
            postJoinButton = post.find(attrs={"data-tag": "join-button"})
            postLocked = False
            if postJoinButton != None:
                postLocked = True

            self.info.postList.append(PatreonPost(postTitleText, postDateText, baseURL + postLink, postLocked))

        print("Scan Done.")