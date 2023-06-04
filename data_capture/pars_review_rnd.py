from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
import time
import re

try:
    city = "rnd"
    # для запуска в фоновом режиме (чтобы убрать эту функцию - надо удалить chrome_options=options)
    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    link = "https://"+city+".repetitors.info/repetitor/"

    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    driver.get(link)
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    file_name = "repetitor_data_" + city + ".csv"
    data = open(file_name, "w")
    data.write("Link;Name;Description;Mark;Subject;Experience\n")
    data.close()


    def pars_page(page_link, subject_title, experience_title):
        retry_index = 0
        while True:
            try:
                driver.get(page_link)
                break
            except WebDriverException:
                print("Retrying.... " + str(retry_index))
                retry_index += 1
                time.sleep(3)

        try:
            paginationTableElement = driver.find_element(By.CLASS_NAME, "ListanketsPaginator")
        except WebDriverException:
            print("nothing to parse")
            return

        paginationText = paginationTableElement.text
        repetitCountText = re.findall(r"\s\d+\.", paginationText)
        repetitCount = int(repetitCountText[0].replace(" ", "").replace(".", ""))

        lastPage = repetitCount // 10

        for i in range(lastPage):
            repetitKeyElements = driver.find_elements(By.CSS_SELECTOR, ".pnmst .deca")

            repetitIndex = 1
            data = open(file_name, "a")
            for repetitKeyElement in repetitKeyElements:
                repetitLink = repetitKeyElement.get_attribute('href')

                description = driver.find_element(By.XPATH,
                                                  "//*[@id=\"MainTD\"]/table[" + str(repetitIndex) + "]/tbody/tr/td[2]")
                mark = driver.find_element(By.XPATH,
                                           "//*[@id=\"MainTD\"]/table[" + str(repetitIndex) + "]/tbody/tr/td[1]")

                # text = repetitLink + ";" + repetitKeyElement.text.replace("\n", " ").replace(";", " ") + ";" + description.text.replace("\n", " ").replace(";", " ") + ";" + mark.text.replace("\n", " ").replace(";", " ") + ";" + subject_title + ";" + experience_title + "\n"

                text = "{};{};{};{};{};{}\n".format(
                    repetitLink,
                    repetitKeyElement.text.replace("\n", " ").replace(";", " "),
                    description.text.replace("\n", " ").replace(";", " "),
                    mark.text.replace("\n", " ").replace(";", " "),
                    subject_title,
                    experience_title
                )

                print(repetitLink)
                data.write(text)
                repetitIndex += 1

            data.close()

            nextPageHref = page_link + "&L=" + str(8 * (i + 1))
            print(nextPageHref)

            retryIndex = 0
            while True:
                try:
                    driver.get(nextPageHref)
                    break
                except WebDriverException:
                    print("Retrying.... " + str(retryIndex))
                    retryIndex += 1
                    time.sleep(3)


    subjects = {
        1: "математика",
        2: "физика",
        3: "информатика",
        4: "программирование",
        5: "химия",
        6: "биология",
        101: "русский язык",
        7: "экономика",
        8: "история",
        9: "обществознание",
        10: "литература",
        11: "география",
        50: "начальная школа",
        102: "английский язык",
        103: "немецкий язык",
        104: "французский язык",
        105: "китайский язык",
        106: "испанский язык",
        107: "итальянский язык",
        109: "японский язык",
        201: "музыка",
        400: "подготовка к школе",
    }
    experiences = {
        50: "Небольшой опыт",
        55: "Средний опыт",
        60: "Школьный учитель",
        65: "Преподаватель курсов",
        70: "Серьёзный опыт",
        75: "Преподаватель вуза",
        80: "Репетитор-эксперт",
        85: "Профессор",
    }

    for sj in subjects:
        for op in experiences:
            path = link + "?sj=" + str(sj) + "&lc=0&ck=0&gn=0&zn=0&op=" + str(op) + "&skd=0"
            print(path)
            pars_page(path, subjects[sj], experiences[op])

finally:
    time.sleep(3)
    driver.quit()
