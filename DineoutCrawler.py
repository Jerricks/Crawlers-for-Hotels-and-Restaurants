import time, os
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from app import app


def dineOut(filter):
    try:
        # chromedriver = "/Documents/chromedriver"
        # os.environ["webdriver.chrome.driver"] = chromedriver
        # driver = webdriver.Chrome(executable_path=r"/home/repusight/Documents/chromedriver")
        driver = webdriver.Chrome()
        driver.get(filter[0]["url1"])
        time.sleep(8)
        driver.maximize_window()
        while driver.find_elements_by_class_name("load_more_review"):
            driver.find_element_by_class_name("load_more_review").click()
        html = driver.page_source
        soup = BeautifulSoup(html)
        driver.close()
        hotelName = filter[0]["propertyName"]
        hotelPlace = filter[0]["Place"]
        data = []
        allReviews = soup.find_all("div", class_="d_review_0")
        for review in allReviews:
            try:
                date = review.find("div", class_="font12").getText()
                date = date[13:]
                pattern = '%d %b %Y '
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
                Rname = review.find("span", class_="font16").getText()
                Rimg = filter[0]["Logo"]
                comment = review.find("div", class_="font14").getText()
                Rat = review.find("div", id="rating_circle_div2")
                Rating = float(Rat.find("span").getText())
                Replied = "R2"
                data.append({"Name": hotelName, "Place": hotelPlace, "Date": date, "Rname": Rname,
                             "Rimg": Rimg, "Comment": comment, "ReviewID": "",
                             "Rating": Rating, "Channel": filter[0]["source"],
                             "icon": "/static/images/dineout-logo.jpg",
                             "Replied": Replied, "Logo": filter[0]["Logo"], "URL": filter[0]["revertURL"],
                             "City": filter[0]["City"], "State": filter[0]["State"], "Country": filter[0]["Country"]})
            except Exception as e:
                print(e)
                pass
    except Exception as e:
        print(e)
    if data:
        dtaFrm = pd.DataFrame(data)
    if not dtaFrm.empty:
        app.config["PROPERTY_COLLECTION"].update({"_id": filter[0]["_id"]}, {"$set": {"lastCrawl": round(time.time())}})
    filename = (
        str(filter[0]["propertyName"]) + "_" + str(filter[0]["Place"]) + "_" + str(filter[0]["source"]) + "_" + str(
            time.strftime("%d-%m-%Y")) + ".csv").replace(" ", "").replace("'", "")
    with open('/home/repusight/data/' + filename, 'a') as f:
        dtaFrm.to_csv(f, sep='|', encoding='utf-8', index=False, header=True)
    print("3-Crawled")
    return "Crawled"
