import time, os
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from app import app


def eveningFlavor(filter):
    data = list()
    # chromedriver = "/Documents/chromedriver"
    # os.environ["webdriver.chrome.driver"] = chromedriver
    # driver = webdriver.Chrome(executable_path=r"/home/repusight/Documents/chromedriver")
    driver = webdriver.Chrome()
    time.sleep(5)

    try:
        driver.find_element_by_xpath('//div[@class = "card-text text-center defaultBlueText"]').click()
    except:
        time.sleep(5)
        driver.get(filter[0]['url1'])
    driver.maximize_window()

    time.sleep(5)
    try:
        driver.find_element_by_xpath('//div[@class = "card-text text-center defaultBlueText"]').click()
    except:
        time.sleep(3)
        driver.find_element_by_xpath('//div[@class = "card-text text-center defaultBlueText"]').click()

    time.sleep(5)

    soup = BeautifulSoup(driver.page_source)
    driver.close()
    review_tiles = soup.find_all('div', {'class': 'home-review-border review-cards'})

    for review_tile in review_tiles:
        date = review_tile.find('span', {'class': 'cust-visited'}).text.strip()
        if date != "":
            pattern = '%d/%m/%Y'
            date = int(time.mktime(time.strptime(date, pattern)))

        if date > filter[0]['lastCrawl']:
            rname = review_tile.find('span', {'class': 'cust-name'}).text.strip('\n')
            review = review_tile.find('div', {'class': 'cust-review'}).find_all('a')
            comment = review[1].text.strip('\n')
            rating = int(review_tile.find('div', {'id': 'review-rating'}).find('span', style='font-size: 16px;').text)
            rimg = review_tile.find_all('img')
            if len(rimg) > 1:
                rimg = rimg[1]
            else:
                rimg = rimg[0]

            try:
                rimg = rimg['src']
            except:
                rimg = filter[0]['Logo']

            data.append(
                {"Name": filter[0]['propertyName'], "Place": filter[0]['Place'], "Date": int(round(date)), "Rname": rname,
                 "Rimg": rimg, "Comment": comment, "ReviewID": "",
                 "Rating": rating, "Channel": filter[0]["source"], "icon": "/static/images/logo-holidayiq.png",
                 "Replied": 'R2', "Logo": filter[0]["Logo"], "URL": filter[0]["revertURL"],
                 "City": filter[0]["City"], "State": filter[0]["State"], "Country": filter[0]["Country"]})

    if len(data) > 0:
        dtaFrm = pd.DataFrame(data)
        if not dtaFrm.empty:
            app.config["PROPERTY_COLLECTION"].update({"_id": filter[0]["_id"]},
                                                     {"$set": {"lastCrawl": round(time.time())}})
        filename = (
            str(filter[0]["propertyName"]) + "_" + str(filter[0]["Place"]) + "_" + str(filter[0]["source"]) + "_" + str(
                time.strftime("%d-%m-%Y")) + ".csv").replace(" ", "").replace("'", "")
        with open('/home/repusight/data/' + filename, 'a') as f:
            dtaFrm.to_csv(f, sep='|', encoding='utf-8', index=False, header=True)
        print("1-Crawled")
        return "Crawled"
    else:
        print("2-Already Updated !!")
        return "Already Updated !!"
