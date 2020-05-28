import time, os
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import math
from app import app


def zomato(filter):
    # This crawler uses both selenium and beautiful soup
    try:
        # chromedriver = "/Documents/chromedriver"   #getting the chrome instance
        # os.environ["webdriver.chrome.driver"] = chromedriver
        # driver = webdriver.Chrome(executable_path=r"/home/repusight/Documents/chromedriver")
        driver = webdriver.Chrome()
        driver.get(filter[0]["url1"])  # getting the url and open page
        time.sleep(8)
        # Maximiazing Browser to window size
        driver.maximize_window()
        time.sleep(8)

        try:
            element = driver.find_element_by_xpath("//*[@id='selectors']/a[2]")
            driver.execute_script("arguments[0].click();", element)
            time.sleep(8)
            totalreviews = driver.find_element_by_xpath("//*[@id='selectors']/a[2]/span").text
        except:
            totalreviews = driver.find_element_by_xpath("//*[@id='selectors']/a/span").text

        # get total load more on page
        count1 = math.floor(int(totalreviews) / 5)
        data = []

        # Click load more
        for count in range(0, count1):
            try:
                x = driver.find_elements_by_xpath("//*[@class='load-more bold ttupper tac cursor-pointer fontsize2']")
                if len(x) != 0:
                    element = driver.find_element_by_xpath(
                        "//*[@class='load-more bold ttupper tac cursor-pointer fontsize2']")
                    driver.execute_script("arguments[0].click();", element)
                    time.sleep(5)
            except (Exception) as e:
                break

        # after clicking all load more all the reviews are loaded and we can extract html code using BS
        html = driver.page_source  # get html code of present page
        soup = BeautifulSoup(html, "lxml")
        hotelName = filter[0]["propertyName"]
        hotelPlace = filter[0]["Place"]

        # Get div contains all the reviews
        mainDiv = soup.find("div", class_="zs-following-list")

        # find all the reviews in mainDiv
        allDiv = mainDiv.find_all("div", class_="res-review-body")
        for div in allDiv:  # For each review get details
            date = div.find("time")["datetime"]
            pattern = '%Y-%m-%d %H:%M:%S'
            date = int(time.mktime(time.strptime(date, pattern)))
            if filter[0]["lastCrawl"] != "" and date <= int(filter[0]["lastCrawl"]):
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
            reviewID = div["data-review_id"]
            rname = div.find("img", class_="avatar")["alt"]
            rimg = div.find("img", class_="avatar")["src"]
            if rimg == "https://b.zmtcdn.com/images/placeholder_200.png":
                rimg = filter[0]["Logo"]
            rating = div.find("div", class_="ttupper")["aria-label"]
            rating = rating[6:]
            comment = div.find("div", class_="ttupper").parent.getText()
            comment = ' '.join([segment for segment in comment.split()])
            comment = comment[6:]
            reply = div.find_all("div", id="rrtr-" + str(reviewID))
            if reply:
                replied = "R1"
            else:
                replied = "R0"
            data.append(
                {"Name": hotelName, "Place": hotelPlace, "Date": date, "Rname": rname,
                 "Rimg": rimg, "Comment": comment, "ReviewID": reviewID,
                 "Rating": rating, "Channel": filter[0]["source"], "icon": "/static/images/zomato.jpg",
                 "Replied": replied, "Logo": filter[0]["Logo"], "URL": filter[0]["revertURL"],
                 "City": filter[0]["City"], "State": filter[0]["State"], "Country": filter[0]["Country"]})
    except Exception as e:
        print(e)
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
