import time, os
from selenium import webdriver
import pandas as pd
import math
from app import app


def expedia(filter):
    # chromedriver = "/Documents/chromedriver"
    # os.environ["webdriver.chrome.driver"] = chromedriver
    # driver = webdriver.Chrome(executable_path=r"/home/repusight/Documents/chromedriver")
    driver = webdriver.Chrome()
    driver.get(filter[0]["url1"])
    driver.maximize_window()
    time.sleep(5)
    hotelName = filter[0]["propertyName"]
    hotelPlace = filter[0]["Place"]
    totalReviews = driver.find_element_by_xpath("/html/body/div[5]/section/section[1]/h2").text
    totalReviews = int(totalReviews.split(" ")[3])
    count = math.ceil(totalReviews / 10)
    data = []
    for i in range(count):
        rinp = driver.find_elements_by_class_name("review")
        for reviews in rinp:
            Date = reviews.find_element_by_class_name("date-posted").text
            Date = Date.split(" ")[1]
            pattern = '%d-%b-%Y'
            Date = int(time.mktime(time.strptime(Date, pattern)))
            if filter[0]["lastCrawl"] != "" and Date <= int(filter[0]["lastCrawl"]):
                if data:
                    dtaFrm = pd.DataFrame(data)
                    driver.close()
                    if not dtaFrm.empty:
                        app.config["PROPERTY_COLLECTION"].update({"_id": filter[0]["_id"]},
                                                                 {"$set": {"lastCrawl": round(time.time())}})
                    filename = (str(filter[0]["propertyName"]) + "_" + str(filter[0]["Place"]) + "_" + str(
                        filter[0]["source"]) + "_" + str(time.strftime("%d-%m-%Y")) + ".csv").replace(" ", "").replace(
                        "'", "")
                    with open('/home/repusight/data/' + filename, 'a') as f:
                        dtaFrm.to_csv(f, sep='|', encoding='utf-8', index=False, header=True)
                    print("1-Crawled")
                    return "Crawled"
                else:
                    driver.close()
                    print("2-Already Updated !!")
                    return "Already Updated !!"
            Rating = reviews.find_element_by_class_name("rating").text
            Rating = Rating.replace("out of 5", "")
            Rating = int(Rating)
            if reviews.find_elements_by_class_name("review-text"):
                Comment = reviews.find_element_by_class_name("review-text").text
            else:
                Comment = "Comment not posted"
            Rname = reviews.find_element_by_class_name("user").text
            if "from" in Rname:
                Rname = Rname[3:Rname.index("from")]
            else:
                Rname = Rname[3:]
            data.append(
                {"Name": hotelName, "Place": hotelPlace, "Date": Date, "Rname": Rname,
                 "Rimg": filter[0]["Logo"], "Comment": Comment, "ReviewID": "",
                 "Rating": Rating, "Channel": filter[0]["source"], "icon": "/static/images/Expedia.svg",
                 "Replied": "R2", "Logo": filter[0]["Logo"], "URL": filter[0]["revertURL"],
                 "City": filter[0]["City"], "State": filter[0]["State"], "Country": filter[0]["Country"]})
        pg = driver.find_elements_by_xpath("//*[@id='next-page-button']")
        if pg:
            driver.find_element_by_xpath("//*[@id='next-page-button']").click()
            time.sleep(5)
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
