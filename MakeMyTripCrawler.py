import time, os
from selenium import webdriver
import pandas as pd
import math
from app import app


def makemytrip(filter):
    # chromedriver = "/Documents/chromedriver"
    # os.environ["webdriver.chrome.driver"] = chromedriver
    # driver = webdriver.Chrome(executable_path=r"/home/repusight/Documents/chromedriver")
    driver = webdriver.Chrome()
    driver.get(filter[0]["url1"])
    time.sleep(8)
    driver.maximize_window()
    time.sleep(5)
    hotelName = filter[0]["propertyName"]
    hotelPlace = filter[0]["Place"]
    driver.find_element_by_xpath("//*[@id='block-ksa-blocks-hotel-content']/div[2]/div/ul/li[4]/a").click()
    time.sleep(4)
    driver.find_element_by_id("filter_0").click()
    time.sleep(4)
    driver.find_element_by_xpath("//*[@id='mmt_reviews_data']/div/div/div[2]/div[1]/span/div/div").click()
    time.sleep(4)
    driver.find_element_by_xpath("//*[@id='drop-down']/li[1]/span").click()
    time.sleep(4)
    totalReviews = int(driver.find_element_by_xpath("//*[@id='filter_0']/span").text.replace("(", "").replace(")", ""))
    count = math.ceil(int(totalReviews) / 5)
    data = []
    todayDate = int(time.time())
    try:
        for i in range(1, count + 1):
            for j in range(1, 6):
                time.sleep(3)
                Date = driver.find_element_by_xpath("//*[@id='all']/div[" + str(j) + "]/div[1]/p[3]").get_attribute(
                    'innerHTML')
                if Date != "":
                    Date = int(int(Date) / 1000)
                    if filter[0]["lastCrawl"] != "" and Date <= int(filter[0]["lastCrawl"]):
                        if data:
                            dtaFrm = pd.DataFrame(data)
                            print(dtaFrm)
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
                Rname = driver.find_element_by_xpath("//*[@id='all']/div[" + str(j) + "]/div[1]/p[2]").text
                Rimg = "http://mmtcdn.com/hcs/assets/img/logo.png"
                Rating = driver.find_element_by_xpath("//*[@id='all']/div[" + str(j) + "]/div[2]/p[2]/span[1]").text
                driver.find_element_by_xpath("//*[@id='all']/div[" + str(j) + "]/div[2]/p[3]/span[2]/a").click()
                comment = driver.find_element_by_xpath("//*[@id='all']/div[" + str(j) + "]/div[2]/p[3]").text
                comment = comment.replace("(less)", "")
                data.append(
                    {"Name": hotelName, "Place": hotelPlace, "Date": Date, "Rname": Rname,
                     "Rimg": Rimg, "Comment": comment, "ReviewID": "",
                     "Rating": Rating, "Channel": filter[0]["source"], "icon": "/static/images/mmt.jpg",
                     "Replied": "R2", "Logo": filter[0]["Logo"], "URL": filter[0]["revertURL"],
                     "City": filter[0]["City"], "State": filter[0]["State"], "Country": filter[0]["Country"]})
            try:
                driver.find_element_by_xpath("//*[@id='all']/div[6]/nav/ul/li[@class='jplist-next']/a").click()
            except:
                pass
    except (Exception) as e:
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
