"""
Scrapes a target Patreon for information with Selenium
"""

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
from datetime import date
import os

# target website
baseURL = "https://www.patreon.com"

target = "https://www.patreon.com/alfabusa"
target2 = "https://www.patreon.com/NarrativeDeclaration"
target3 = "https://www.patreon.com/PartyDemoness"
target4 = "https://www.patreon.com/rutabega"

selectTarget = "notarealsite.com"

# Patreon identifiers
titleClass = "sc-jgrJph.YCXEB"
subtitleClass = "sc-bdvvtL.lhrfPG"
memberCountXPath = "//span[@data-tag='patron-count']"
postCountXPath = "//span[@data-tag='creation-count']"
incomeXPath = "//span[@data-tag='earnings-count']"

seeMoreXPath = "//*[@id='renderPageContentWrapper']/div[1]/div/div/div[3]/div[2]/div[2]/div/div[5]/button"
ageConfirmXPath = "//button[@data-tag='age-confirmation-button']"

# enable headless mode in Selenium
options = Options()
options.add_argument("--headless=new")

driver = webdriver.Chrome(options=options)

# sleep until page is fully loaded
print(f"Initiating Webscrape of {selectTarget}...\n")
driver.get(selectTarget)

try:
    WebDriverWait(driver, 5).until(
        EC.text_to_be_present_in_element((By.XPATH, seeMoreXPath), "See more posts")
    )
except TimeoutException:
    print("A timeout has occured. Attempting Age Confirmation Check...")
    ageConfirm = driver.find_element(By.XPATH, ageConfirmXPath)
    ageConfirm.click()
    print("Success! Proceeding.\n")


# display all posts
print("Displaying all posts...")


def attemptClick(button):
    time.sleep(1)
    # print("END Start")
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
    # print("END Stop")
    time.sleep(1)
    # print("Click Start")
    button.click()
    # print("Click Stop")


try:
    WebDriverWait(driver, 5).until(
        EC.text_to_be_present_in_element((By.XPATH, seeMoreXPath), "See more posts")
    )

    postTotal = float(
        driver.find_element(By.XPATH, postCountXPath)
        .text.split(" ")[0]
        .replace(",", "")
    )
    clickEstimate = int(math.ceil((postTotal - 20.0) / 20.0))

    seeMore = driver.find_element(By.XPATH, seeMoreXPath)
    clickCounter = 1
    seeMore.click()
    print(f"Click {clickCounter} / {clickEstimate}")
    clickCounter += 1

    while True:
        try:
            attemptClick(seeMore)
            print(f"Click {clickCounter} / {clickEstimate}")
            clickCounter += 1
        except ElementClickInterceptedException:
            print("Error: Click Intercepted. Retrying...")
        except StaleElementReferenceException:
            print("End of Page found. Proceeding...\n")
            break
except NoSuchElementException:
    print("Error: Cannot find button")


patreonIncome = None
patreonMemberCount = None

# scraping information
patreonTitle = driver.find_element(By.CLASS_NAME, titleClass).text
patreonSubtitle = driver.find_element(By.CLASS_NAME, subtitleClass).text

try:
    patreonMemberCount = int(
        driver.find_element(By.XPATH, memberCountXPath).text.split(" ")[0].replace(",", "")
    )
except NoSuchElementException:
    print("Member Count not found\n")

patreonPostCount = int(
    driver.find_element(By.XPATH, postCountXPath).text.split(" ")[0].replace(",", "")
)

try:
    patreonIncome = driver.find_element(By.XPATH, incomeXPath).text
except NoSuchElementException:
    print("Income not found\n")

soup = BeautifulSoup(driver.page_source, "html.parser")
# print(soup.prettify())

recentPosts = soup.find(attrs={"data-tag": "all-posts-layout"})
postList = recentPosts.find_all(attrs={"data-tag": "post-card"})

tempC = 1
postInfoList = []
# print(len(postList))
for post in postList:
    # print(f"Processing Post {tempC} / {len(postList)}")
    tempC += 1

    # print(post.prettify())

    postTitle = post.find(attrs={"data-tag": "post-title"})
    postTitleText = "Title Not Found."
    if postTitle != None:

        sanitizedPostTitleText = postTitle.text.replace('\"', '\"\"')
        postTitleText = sanitizedPostTitleText

    postDate = post.find(attrs={"data-tag": "post-published-at"})
    postLink = postDate["href"]

    postJoinButton = post.find(attrs={"data-tag": "join-button"})
    postLocked = False
    if postJoinButton != None:
        postLocked = True

    postInfoList.append([postTitleText, postDate.text, postLink, postLocked])


print()

# display data
"""
counter = 1
for info in postInfoList:
    print(f"Post {counter}\nTitle: {info[0]}\nDate: {info[1]}\nLink: {baseURL + info[2]}\nLocked: {info[3]}\n")
    counter += 1
"""
print(f"Patreon: {patreonTitle}\n{patreonSubtitle}\n")
if patreonMemberCount is not None:
    print(f"Member Count: {patreonMemberCount}")
else:
    print("Member Count not found")
print(f"Post Count: {len(postInfoList)}/{patreonPostCount}")
if patreonIncome is not None:
    print(f"Income: {patreonIncome}")
else:
    print("Income not found")

# record data
output = "output"
if not os.path.exists(output):
    os.makedirs(output)    

fileName = f"{output}/{selectTarget.split('/').pop()}_results_{date.today()}.csv"
print(f"\nSaving Results to {fileName}...")

with open(fileName, "w", encoding="utf8") as f:
    f.write(f'Patreon,{patreonTitle},"{patreonSubtitle}"\n')
    f.write(f"Member Count,{patreonMemberCount}\n")
    f.write(f"Post Count,{patreonPostCount}\n")
    if patreonIncome != -1:
        f.write(f'Income,"{patreonIncome}"\n')
    else:
        f.write("Income,N/A\n")

    counter = 1
    f.write("Post,Title,Date,Link,Locked\n")
    for info in postInfoList:
        f.write(f'{counter},"{info[0]}","{info[1]}",{baseURL + info[2]},{info[3]}\n')
        counter += 1

# exit/cleanup
print("Done.")
# input()
driver.close()
print("Exitting...")
