import time, os
from selenium import webdriver
import pandas as pd
from bs4 import BeautifulSoup
from app import app


def burrp(filter):
    try:
        # chromedriver = "/Documents/chromedriver"
        # os.environ["webdriver.chrome.driver"] = chromedriver
        # driver = webdriver.Chrome(executable_path=r"/home/repusight/Documents/chromedriver")
        driver = webdriver.Chrome()
        driver.get(filter[0]["url1"])
        mores = driver.find_elements_by_link_text("Read more")
        for more in mores:
            driver.execute_script("arguments[0].click();", more)
            time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        restaurantName = filter[0]["propertyName"]
        restaurantPlace = filter[0]["Place"]
        soup = soup.find_all("div", class_="review-pane-inner clearfix")
        data = []
        for div in soup:
            date = div.find_next("div", class_="author-name").find_next("span").getText()
            pattern = '%B %d,%Y'
            date = int(time.mktime(time.strptime(date, pattern)))
            if filter[0]["lastCrawl"] != "" and date <= int(filter[0]["lastCrawl"]):
                if data:
                    dtaFrm = pd.DataFrame(data)
                    driver.close()
                    if not dtaFrm.empty:
                        app.config["PROPERTY_COLLECTION"].update({"_id": filter[0]["_id"]},
                                                                 {"$set": {"lastCrawl": round(time.time())}})
                    filename = (str(filter[0]["propertyName"]) + "_" + str(filter[0]["Place"]) + "_" + str(
                        filter[0]["source"]) + "_" + str(time.strftime("%d-%m-%Y")) + ".csv").replace(" ", "").replace("'", "")
                    with open('/home/repusight/data/' + filename, 'a') as f:
                        dtaFrm.to_csv(f, sep='|', encoding='utf-8', index=False, header=True)
                    print("1-Crawled")
                    return "Crawled"
                else:
                    driver.close()
                    print("2-Already Updated !!")
                    return "Already Updated !!"
            rimg = div.find_next("div", class_="author-pic").find_next("img")['src']
            if rimg == "http://www.burrp.com/images/default_user.jpg":
                rimg = filter[0]["Logo"]
            rname = div.find_next("div", class_="author-name").find_next("a").getText()
            comment = div.find_next("div", class_="review_con").getText()
            rating = div.find_next("span", class_="badge badge-md right").getText()
            if rating == "--":
                rating = 0
            replydiv = div.find("div", class_="rev_reply_box")
            if replydiv != None:
                Replied = "R1"
            else:
                Replied = "R0"
            data.append(
                {"Name": restaurantName, "Place": restaurantPlace, "Date": date, "Rname": rname,
                 "Rimg": rimg, "Comment": comment, "ReviewID": "",
                 "Rating": rating, "Channel": filter[0]["source"], "icon": "/static/images/burrp-new-logo.jpg",
                 "Replied": Replied, "Logo": filter[0]["Logo"], "URL": filter[0]["revertURL"],
                 "City": filter[0]["City"], "State": filter[0]["State"], "Country": filter[0]["Country"]})
    except Exception as e:
        print(e)
        return "Something went wrong !!"
    if data:
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