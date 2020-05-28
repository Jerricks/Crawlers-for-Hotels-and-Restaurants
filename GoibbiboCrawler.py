import time, os
from selenium import webdriver
import pandas as pd
import math
from app import app


def goibibo(filter):
    # chromedriver = "/Documents/chromedriver"
    # os.environ["webdriver.chrome.driver"] = chromedriver
    # driver = webdriver.Chrome(executable_path=r"/home/repusight/Documents/chromedriver")
    driver = webdriver.Chrome()
    driver.get(filter[0]["url1"])
    time.sleep(8)
    driver.maximize_window()
    data = []
    hotelName = filter[0]["propertyName"]
    hotelPlace = filter[0]["Place"]
    datalink = driver.find_element_by_xpath("//*[@id='rnrNav']/ul/li[2]/a")
    driver.execute_script("arguments[0].click();", datalink)
    temp1 = driver.find_element_by_xpath("//*[@id='Reviews']/div[1]/div[1]/div[1]/span[2]").text
    temp1 = temp1.split(" ")[0]
    pageCount = math.ceil(int(temp1) / 5)

    for page in range(1, pageCount + 1):
        try:
            for reviewer in range(1, 6):
                try:
                    date = driver.find_element_by_xpath(
                        "//*[@id='Reviews']/div[3]/div[" + str(reviewer) + "]/div[1]/span[2]/span[4]").text
                    pattern = '%Y, %d %b'
                    date = int(time.mktime(time.strptime(date, pattern)))
                except:
                    date = driver.find_element_by_xpath(
                        "//*[@id='Reviews']/div[3]/div[" + str(reviewer) + "]/div[1]/span[2]/span[3]").text
                    pattern = '%Y, %d %b'
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
                reviewerName = driver.find_element_by_xpath(
                    "//*[@id='Reviews']/div[3]/div[" + str(reviewer) + "]/div[1]/span[2]/span[1]").text
                try:
                    reviewerImage = driver.find_element_by_xpath(
                        "//*[@id='Reviews']/div[3]/div[" + str(reviewer) + "]/div[1]/span[1]/img").get_attribute('src')
                except:
                    reviewerImage = filter[0]["Logo"]
                try:
                    rating = driver.find_element_by_xpath(
                        "//*[@id='Reviews']/div[3]/div[" + str(reviewer) + "]/div[1]/span[2]/span[3]/span/strong").text
                except:
                    rating = driver.find_element_by_xpath(
                        "//*[@id='Reviews']/div[3]/div[" + str(reviewer) + "]/div[1]/span[2]/span[2]/span/strong").text
                try:
                    try:
                        driver.find_element_by_xpath(
                            "//*[@id='Reviews']/div[3]/div[" + str(reviewer) + "]/div[2]/div/a").click()
                        comment = driver.find_element_by_xpath(
                            "//*[@id='Reviews']/div[3]/div[" + str(reviewer) + "]/div[2]/div[1]/p").text
                    except:
                        comment = driver.find_element_by_xpath(
                            "//*[@id='Reviews']/div[3]/div[" + str(reviewer) + "]/div[2]/div[1]/p").text
                except:
                    comment = "No Comment"
                replied = "R"
                try:
                    if driver.find_element_by_xpath(
                                            "//*[@id='Reviews']/div[3]/div[" + str(reviewer) + "]/div[2]/div[3]/p"):
                        replied = "R1"
                except:
                    replied = "R0"
                if comment == "No Comment":
                    replied = "R2"
                data.append(
                    {"Name": hotelName, "Place": hotelPlace, "Date": date, "Rname": reviewerName,
                     "Rimg": reviewerImage, "Comment": comment, "ReviewID": "",
                     "Rating": rating, "Channel": filter[0]["source"], "icon": "/static/images/goibibo.jpg",
                     "Replied": replied, "Logo": filter[0]["Logo"], "URL": filter[0]["revertURL"],
                     "City": filter[0]["City"], "State": filter[0]["State"], "Country": filter[0]["Country"]})
            nextpagelink = driver.find_element_by_xpath(
                "//*[@id='Reviews']/div[3]/nav/ul/li[@class='active']/following-sibling::li")
            driver.execute_script("arguments[0].click();", nextpagelink)
        except (Exception) as e:
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
