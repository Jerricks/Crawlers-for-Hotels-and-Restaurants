import time, os
from selenium import webdriver
import pandas as pd
import math
from app import app
from selenium.common.exceptions import NoSuchElementException


def agoda(filter):
    # chromedriver = "/Documents/chromedriver"
    # os.environ["webdriver.chrome.driver"] = chromedriver
    # driver = webdriver.Chrome(executable_path=r"/home/repusight/Documents/chromedriver")
    driver = webdriver.Chrome()
    driver.get(filter[0]["url1"])
    time.sleep(8)
    driver.maximize_window()
    data = []
    try:
        hotelName = filter[0]["propertyName"]
        hotelPlace = filter[0]["Place"]
        reviewClick = driver.find_elements_by_xpath("//*[@id='property-root']/div/div[1]/div[2]/div[2]/span[2]")
        if reviewClick:
            totalReviews = driver.find_element_by_xpath(
                "//*[@id='property-root']/div/div[1]/div[2]/div[2]/span[2]").text
            totalReviews = int(totalReviews)
            pages = math.ceil(totalReviews / 10)
            try:
                driver.find_element_by_xpath("//*[@id='property-root']/div/div[1]/div[2]/div[2]/span").click()
            except Exception as e:
                driver.execute_script('document.getElementById("page-backdrop").className = "inactive";')
                print(e)
                try:
                    driver.find_element_by_xpath("//*[@id='property-root']/div/div[1]/div[2]/div[2]/span").click()
                except Exception as po:
                    print(po)
                pass
            for page in range(pages):
                allReviews = driver.find_elements_by_class_name("Review-comment")
                idList = []
                for review in allReviews:
                    id = review.get_attribute("id")
                    idList.append(id)
                for everyId in idList:
                    date = driver.find_element_by_class_name('Review-statusBar-date ').text
                    date1 = date
                    date = date.replace("Reviewed ", "")
                    if date != '':
                        pattern = '%B %d, %Y'
                        date = int(time.mktime(time.strptime(date, pattern)))
                    if filter[0]["lastCrawl"] != "" and date <= int(filter[0]["lastCrawl"]):
                        if data:
                            dtaFrm = pd.DataFrame(data)
                            driver.close()
                            if not dtaFrm.empty:
                                app.config["PROPERTY_COLLECTION"].update({"_id": filter[0]["_id"]},
                                                                         {"$set": {"lastCrawl": round(time.time())}})
                            filename = (str(filter[0]["propertyName"]) + "_" + str(filter[0]["Place"]) + "_" + str(
                                filter[0]["source"]) + "_" + str(time.strftime("%d-%m-%Y")) + ".csv").replace(" ",
                                                                                                              "").replace(
                                "'", "")
                            with open('/home/repusight/data/' + filename, 'a') as f:
                                dtaFrm.to_csv(f, sep='|', encoding='utf-8', index=False, header=True)
                            print("1-Crawled")
                            return "Crawled"
                        else:
                            driver.close()
                            print("2-Already Updated !!")
                            return "Already Updated !!"
                    Rname = driver.find_element_by_xpath(
                        "//*[@id='" + str(everyId) + "']/div[@class = 'Review-comment-left']/div/div[@data-info-type = 'reviewer-name']/strong").text
                    Rimg = filter[0]["Logo"]
                    Rating = driver.find_element_by_xpath("//*[@id='" + str(everyId) + "']/div[@class = 'Review-comment-left']/div/div[@class = 'Review-comment-score']").text
                    Rating = math.floor(int(float(Rating)) / 2)
                    comment = driver.find_element_by_xpath("//*[@id='" + str(everyId) + "']/div[@class = 'Review-comment-right']/div[@class = 'Review-comment-bubble']").text
                    comment = comment.replace(date1, '')
                    reviewId = everyId.replace("review-", "")
                    data.append(
                        {"Name": hotelName, "Place": hotelPlace, "Date": date, "Rname": Rname,
                         "Rimg": Rimg, "Comment": comment, "ReviewID": reviewId,
                         "Rating": Rating, "Channel": filter[0]["source"],
                         "icon": "/static/images/Agoda-logo.png",
                         "Replied": "R2", "Logo": filter[0]["Logo"], "URL": filter[0]["revertURL"],
                         "City": filter[0]["City"], "State": filter[0]["State"], "Country": filter[0]["Country"]})
                try:
                    driver.find_element_by_class_name("ficon-carrouselarrow-right").click()
                except NoSuchElementException:
                    break
                time.sleep(4)
    except Exception as e:
        print(e)
        pass
    dtaFrm = pd.DataFrame(data)
    driver.close()
    if not dtaFrm.empty:
        app.config["PROPERTY_COLLECTION"].update({"_id": filter[0]["_id"]}, {"$set": {"lastCrawl": round(time.time())}})
    filename = (
        str(filter[0]["propertyName"]) + "_" + str(filter[0]["Place"]) + "_" + str(filter[0]["source"]) + "_" + str(
            time.strftime("%d-%m-%Y")) + ".csv").replace(" ", "").replace("'", "")
    with open('/home/repusight/data/' + filename, 'a') as f:
        dtaFrm.to_csv(f, sep='|', encoding='utf-8', index=False, header=True)
    print("3-Crawled")
    return "Crawled"
