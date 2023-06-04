from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
import time
import re

try:
    # для запуска в фоновом режиме (чтобы убрать эту функцию - надо удалить chrome_options=options)
    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    link = "https://spb.repetitors.info/repetitor/"

    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    driver.get(link)
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    paginationTableElement = driver.find_element(By.CLASS_NAME, "ListanketsPaginator")
    paginationText = paginationTableElement.text
    repetitCountText = re.findall(r"\s\d+\.", paginationText)
    repetitCount = int(repetitCountText[0].replace(" ", "").replace(".",""))

    lastPage = repetitCount//10

    repetitLinkPattern = re.compile(r'p=[a-zA-Z]+')
    pattern = re.compile(r'Показаны отзывы:\s\d+–\d+\sиз\s\d+\.')

    data = open("data_spb.csv", "w")
    data.write("commentsLink, index, comment, mark\n")
    data.close()

    for i in range(lastPage):
        repetitKeyElements = driver.find_elements(By.CSS_SELECTOR, ".pnmst .deca")

        repetitCommentLinks = []
        for repetitKeyElement in repetitKeyElements:
            repetitCommentLink = repetitKeyElement.get_attribute('href').replace("/repetitor/", "/comments.php")
            repetitCommentLinks.append(repetitCommentLink)

        for repetitCommentLink in repetitCommentLinks:
            print(repetitCommentLink)

            retryIndex = 0
            while True:
                try:
                    driver.get(repetitCommentLink)
                    break
                except WebDriverException:
                    print("Retrying.... "+str(retryIndex))
                    retryIndex +=1
                    time.sleep(3)

            currentUrl = driver.current_url
            match = repetitLinkPattern.search(currentUrl)
            if match == None:
                continue

            src = driver.page_source
            match = pattern.search(src)
            if match == None:
                continue

            commentPaginationText = match[0]
            commentCountText = re.findall(r"\s\d+\.", commentPaginationText)
            commentCount = int(commentCountText[0].replace(" ", "").replace(".",""))

            if commentCount <= 20:
                lastCommentPage = 1
            else:
                lastCommentPage = commentCount // 20


            for j in range(lastCommentPage):
                nextCommentPageHref = repetitCommentLink + "&L=" + str(20 * (j))

                print(nextCommentPageHref)

                retryIndex = 0
                while True:
                    try:
                        driver.get(nextCommentPageHref)
                        break
                    except WebDriverException:
                        print("Retrying.... " + str(retryIndex))
                        retryIndex += 1
                        time.sleep(3)

                currentUrl = driver.current_url
                match = repetitLinkPattern.search(currentUrl)
                if match == None:
                    continue

                commentDescriptionElements = driver.find_elements(By.XPATH, "//*[@id=\"CommentsTB\"]/tbody/tr[2]/td/div")
                markElements = driver.find_elements(By.XPATH, "//*[@id=\"CommentsTB\"]/tbody/tr[3]/td")

                data = open("data_spb.csv", "a")
                for g in range(len(commentDescriptionElements)):
                    commentText = commentDescriptionElements[g].text.replace(",","").replace("\n", " ")
                    markText = markElements[g].text

                    text = nextCommentPageHref + ", " + str(g) + ", " + commentText + ", " + markText + "\n"
                    data.write(text)

                data.close()

        nextPageHref = link + "?L=" + str(8*(i+1))
        print(nextPageHref)

        retryIndex = 0
        while True:
            try:
                driver.get(nextPageHref)
                break
            except WebDriverException:
                print("Retrying.... "+str(retryIndex))
                retryIndex += 1
                time.sleep(3)


finally:
    time.sleep(3)
    driver.quit()
