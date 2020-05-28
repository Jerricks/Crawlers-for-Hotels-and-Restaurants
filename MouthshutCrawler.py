import time, os
from selenium import webdriver
import pandas as pd
import math
import dateparser
from app import app


def mouthshut(filter):
    try:
        # chromedriver = "/Documents/chromedriver"
        # os.environ["webdriver.chrome.driver"] = chromedriver
        # driver = webdriver.Chrome(executable_path=r"/home/repusight/Documents/chromedriver")
        driver = webdriver.Chrome()
        driver.get(filter[0]["url1"] + filter[0]["url2"])
        driver.maximize_window()
        time.sleep(8)
        data = []
        restaurantName = filter[0]["propertyName"]
        restaurantPlace = filter[0]["Place"]
        totalreviews = driver.find_element_by_class_name("reviews").text
        totalreviews = totalreviews.split(" ")[0]
        totalPages = math.ceil(int(totalreviews) / 20)
        for pages in range(1, totalPages + 1):
            mores = driver.find_elements_by_link_text("Read More")
            for more in mores:
                more.click()
                time.sleep(2)
            for i in range(0, 20):
                try:
                    if i <= 9:
                        date = driver.find_element_by_id(
                            "ctl00_ctl00_ContentPlaceHolderFooter_ContentPlaceHolderBody_rptreviews_ctl0" + str(
                                i) + "_smdatetime").text
                        if "days ago" in date:
                            date = str(dateparser.parse(date))
                            date = int(time.mktime(time.strptime(date, '%Y-%m-%d %H:%M:%S.%f')))
                        else:
                            pattern = '%b %d, %Y %I:%M %p'
                            date = int(time.mktime(time.strptime(date, pattern)))
                        if filter[0]["lastCrawl"] != "" and date <= int(filter[0]["lastCrawl"]):
                            if data:
                                dtaFrm = pd.DataFrame(data)
                                driver.close()
                                if not dtaFrm.empty:
                                    app.config["PROPERTY_COLLECTION"].update({"_id": filter[0]["_id"]},
                                                                             {"$set": {
                                                                                 "lastCrawl": round(time.time())}})
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
                            "//*[@id='ctl00_ctl00_ContentPlaceHolderFooter_ContentPlaceHolderBody_rptreviews_ctl0" + str(
                                i) + "_divProfile']/p[1]").text
                        Rimg = driver.find_element_by_xpath(
                            "//*[@id='ctl00_ctl00_ContentPlaceHolderFooter_ContentPlaceHolderBody_rptreviews_ctl0" + str(
                                i) + "_divProfile']/div[1]/a/img").get_attribute("src")
                        Ratingpara = driver.find_element_by_xpath(
                            "//*[@id='ctl00_ctl00_ContentPlaceHolderFooter_ContentPlaceHolderBody_rptreviews_ctl0" + str(
                                i) + "_lireviewdetails']/p")
                        Rating = len(Ratingpara.find_elements_by_class_name("rated-star"))
                        comment = driver.find_element_by_xpath(
                            "//*[@id='ctl00_ctl00_ContentPlaceHolderFooter_ContentPlaceHolderBody_rptreviews_ctl0" + str(
                                i) + "_lireviewdetails']/div[2]").text
                    else:
                        date = driver.find_element_by_id(
                            "ctl00_ctl00_ContentPlaceHolderFooter_ContentPlaceHolderBody_rptreviews_ctl" + str(
                                i) + "_smdatetime").text
                        if "days ago" in date:
                            date = str(dateparser.parse(date))
                            date = int(time.mktime(time.strptime(date, '%Y-%m-%d %H:%M:%S.%f')))
                        else:
                            pattern = '%b %d, %Y %I:%M %p'
                            date = int(time.mktime(time.strptime(date, pattern)))
                        Rname = driver.find_element_by_xpath(
                            "//*[@id='ctl00_ctl00_ContentPlaceHolderFooter_ContentPlaceHolderBody_rptreviews_ctl" + str(
                                i) + "_divProfile']/p[1]").text
                        Rimg = driver.find_element_by_xpath(
                            "//*[@id='ctl00_ctl00_ContentPlaceHolderFooter_ContentPlaceHolderBody_rptreviews_ctl" + str(
                                i) + "_divProfile']/div[1]/a/img").get_attribute("src")
                        if Rimg == "http://www.mouthshut.com/Images/COMMON/female-80X80.gif" or Rimg == "http://www.mouthshut.com/Images/COMMON/male-80X80.gif":
                            Rimg = filter[0]["Logo"]
                        Ratingpara = driver.find_element_by_xpath(
                            "//*[@id='ctl00_ctl00_ContentPlaceHolderFooter_ContentPlaceHolderBody_rptreviews_ctl" + str(
                                i) + "_lireviewdetails']/p")
                        Rating = len(Ratingpara.find_elements_by_class_name("rated-star"))
                        comment = driver.find_element_by_xpath(
                            "//*[@id='ctl00_ctl00_ContentPlaceHolderFooter_ContentPlaceHolderBody_rptreviews_ctl" + str(
                                i) + "_lireviewdetails']/div[2]").text
                    data.append(
                        {"Name": restaurantName, "Place": restaurantPlace, "Date": date, "Rname": Rname,
                         "Rimg": Rimg, "Comment": comment, "ReviewID": "",
                         "Rating": Rating, "Channel": filter[0]["source"],
                         "icon": "/static/images/logo-ms.gif",
                         "Replied": "R2", "Logo": filter[0]["Logo"], "URL": filter[0]["revertURL"],
                         "City": filter[0]["City"], "State": filter[0]["State"], "Country": filter[0]["Country"]})
                except Exception as e:
                    print(e)
            driver.find_element_by_link_text("Next").click()
            time.sleep(5)
    except Exception as e:
        print(e)
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
