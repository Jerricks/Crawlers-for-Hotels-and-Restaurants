import time, os
from selenium import webdriver
import pandas as pd
import math
from app import app
import dateparser


def googleReview(filter):
    # chromedriver = "/Documents/chromedriver"
    # os.environ["webdriver.chrome.driver"] = chromedriver
    # driver = webdriver.Chrome(executable_path=r"/home/repusight/Documents/chromedriver")
    driver = webdriver.Chrome()
    driver.get(filter[0]["url1"])
    time.sleep(5)
    data = []
    try:
        r_link = driver.find_element_by_xpath('//a[@data-reply_source="local-search-reviews-list"]')
        driver.execute_script("return arguments[0].scrollIntoView();", r_link)
        r_link.click()
    except:
        driver.find_element_by_xpath('//a[@data-reply_source="local-search-reviews-list"]').click()
    # try:
    #         reviewlink = driver.find_element_by_xpath(
    #             "//*[@id='rhs_block']/div/div[1]/div/div[1]/div[2]/div[6]/div/span[3]/span/a/span")
    #     except:
    #         reviewlink = driver.find_element_by_xpath(
    #             "//*[@id='rhs_sblock']/div[1]/div[1]/div/div[1]/div[2]/div[6]/div/span[3]/span/a/span")
    #     try:
    #         reviewlink = driver.find_element_by_xpath(
    #             "//*[@id='rhs_block']/div/div[1]/div/div[1]/div[2]/div[4]/div/span[3]/span/a/span")
    #     except:
    #         reviewlink = driver.find_element_by_xpath(
    #             "//*[@id='rhs_block']/div/div[1]/div/div[1]/div[2]/div[1]/div/div[2]/div[2]/div/div/span[2]/a/span")
    # except:
    #     reviewlink = driver.find_element_by_xpath(
    #         "//*[@id='rhs_block']/div/div[1]/div/div[1]/div[2]/div[1]/div/div[2]/div[2]/div/div/span[2]/a/span")
    # driver.execute_script("arguments[0].click();", reviewlink)
    time.sleep(5)
    driver.find_element_by_xpath("//*[@id='gsr']/g-lightbox/div[2]/div[3]/div/div/div/div[1]/div[3]/div[2]").click()
    driver.find_element_by_xpath("//*[@id='lb']/div/g-menu/g-menu-item[2]").click()
    time.sleep(5)
    hotelName = filter[0]["propertyName"]
    hotelPlace = filter[0]["Place"]
    temp1 = driver.find_element_by_xpath(
        "//*[@id='gsr']/g-lightbox/div[2]/div[3]/div/div/div/div[1]/div[3]/div[1]/div/span").text.replace(",", "")
    temp1 = temp1.split(" ")[0]
    temp1 = int(temp1)
    scroll_time = math.ceil(int(temp1) / 10)
    scroll = driver.find_element_by_class_name("review-dialog-list")
    for num in range(1, scroll_time + 1):
        for i in range(1, 11):
            print(num, i)
            try:
                try:
                    if driver.find_element_by_xpath("//*[@id='reviewSort']/div[" + str(num) + "]/div[3]/div[" + str(
                            i) + "]/div[1]/div[3]/div[1]/span[1]"):
                        date1 = driver.find_element_by_xpath(
                            "//*[@id='reviewSort']/div[" + str(num) + "]/div[3]/div[" + str(
                                i) + "]/div[1]/div[3]/div[1]/span[1]").text
                    else:
                        date1 = driver.find_element_by_xpath(
                            "//*[@id='reviewSort']/div[" + str(num) + "]/div[3]/div[" + str(
                                i) + "]/div[1]/div[3]/div[1]/span[1]").text
                    if date1 == "in the last week":
                        date1 = "7 days ago"
                    date2 = dateparser.parse(date1)
                    date3 = str(date2)
                    date = int(time.mktime(time.strptime(date3, '%Y-%m-%d %H:%M:%S.%f')))
                except:
                    date2 = dateparser.parse("24 hours ago")
                    date3 = str(date2)
                    date = int(time.mktime(time.strptime(date3, '%Y-%m-%d %H:%M:%S.%f')))
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
                try:
                    reviewerName = driver.find_element_by_xpath(
                        "//*[@id='reviewSort']/div[" + str(num) + "]/div[3]/div[" + str(i) + "]/div[1]/div[1]/a").text
                except:
                    reviewerName = None
                try:
                    moretext = driver.find_element_by_xpath(
                        "//*[@id='reviewSort']/div[" + str(num) + "]/div[3]/div[" + str(
                            i) + "]/div[1]/div[3]/div/span/span[1]/a")
                    driver.execute_script("arguments[0].click();", moretext)
                    comment = driver.find_element_by_xpath(
                        "//*[@id='reviewSort']/div[" + str(num) + "]/div[3]/div[" + str(
                            i) + "]/div[1]/div[3]/div/span/span[2]").text
                except:
                    comment = driver.find_element_by_xpath(
                        "//*[@id='reviewSort']/div[" + str(num) + "]/div[3]/div[" + str(
                            i) + "]/div[1]/div[3]/div[2]/span").text
                if comment == "":
                    comment = "No Comment"
                try:
                    rating = driver.find_element_by_xpath(
                        "//*[@id='reviewSort']/div[" + str(num) + "]/div[3]/div[" + str(
                            i) + "]/div[1]/div[3]/div[1]/g-review-stars/span").get_attribute("aria-label")
                    rating = rating[6:9]
                except Exception as e:
                    print(e)
                    rating = 0
                try:
                    rimg = driver.find_element_by_xpath(
                        "//*[@id='reviewSort']/div[" + str(num) + "]/div[3]/div[" + str(i) + "]/a/img").get_attribute(
                        "src")
                except:
                    rimg = filter[0]["Logo"]
                if driver.find_elements_by_xpath("//*[@id='reviewSort']/div[" + str(num) + "]/div[3]/div[" + str(
                        i) + "]/div[3]/div[1]/strong"):
                    Replied = "R1"
                else:
                    Replied = "R0"
                data.append(
                    {"Name": hotelName, "Place": hotelPlace, "Date": date, "Rname": reviewerName,
                     "Rimg": rimg, "Comment": comment, "ReviewID": None,
                     "Rating": rating, "Channel": filter[0]["source"], "icon": "/static/images/google.jpg",
                     "Replied": Replied, "Logo": filter[0]["Logo"], "URL": filter[0]["revertURL"],
                     "City": filter[0]["City"], "State": filter[0]["State"], "Country": filter[0]["Country"]})
            except Exception as e:
                print(e)
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll)
            time.sleep(3)
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
