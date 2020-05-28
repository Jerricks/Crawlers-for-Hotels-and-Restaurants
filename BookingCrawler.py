import time, os
from selenium import webdriver
import pandas as pd
import math
from app import app


def login_credentials(filter):
    name = filter[0]['propertyName']
    place = filter[0]['Place']
    city = filter[0]['City']
    channel = filter[0]['source']
    if name in ["Ammi's Biryani", "RICE BAR", "Sultan's Biryani"]:
        details = list(app.config["REPLYCREDENTIALS_COLLECTION"].find({'Name': name, 'City': city, 'Channel': channel}))
    else:
        details = app.config["REPLYCREDENTIALS_COLLECTION"].find({'Name': name, 'Place': place, 'City': city, 'Channel': channel})
    return details


def booking(filter):
    driver = webdriver.Chrome()
    # chromedriver = "/Documents/chromedriver"
    # os.environ["webdriver.chrome.driver"] = chromedriver
    # driver = webdriver.Chrome(executable_path=r"/home/repusight/Documents/chromedriver")
    driver.get(filter[0]["url1"])
    driver.maximize_window()
    time.sleep(10)
    hotelName = filter[0]["propertyName"]
    hotelPlace = filter[0]["Place"]
    reviewtablink = driver.find_element_by_xpath("//*[@id='show_reviews_tab']")
    if reviewtablink:
        driver.execute_script("arguments[0].click();", reviewtablink)
    else:
        pass
    time.sleep(10)
    totalReviews = driver.find_element_by_xpath("//*[@id='review_list_score']/span[1]/span/span[2]/span[2]").text
    totalReviews = totalReviews.split(" ")[0]
    totalReviews = int(totalReviews)
    count = math.ceil(totalReviews/10)
    driver.find_element_by_xpath("//*[@id='review_sort']/option[2]").click()
    time.sleep(10)
    data = []
    for pages in range(count+1):
        count = 0
        for i in range(1,11):
            count += 1
            if count == 1:
                continue
            rev = driver.find_element_by_xpath("//*[@id='review_list_page_container']/ul/li[" + str(i) + "]")
            date = rev.find_element_by_class_name("review_item_date").text
            pattern = '%d %B %Y'
            date = int(time.mktime(time.strptime(date, pattern)))
            if filter[0]["lastCrawl"] != "" and date <= int(filter[0]["lastCrawl"]):
                if data:
                    dtaFrm = pd.DataFrame(data)
                    driver.close()
                    if not dtaFrm.empty:
                        app.config["PROPERTY_COLLECTION"].update({"_id": filter[0]["_id"]},
                                                                 {"$set": {"lastCrawl": round(time.time())}})
                    filename = (
                        str(filter[0]["propertyName"]) + "_" + str(filter[0]["Place"]) + "_" + str(
                            filter[0]["source"]) + "_" + str(
                            time.strftime("%d-%m-%Y")) + ".csv").replace(" ", "").replace("'", "")
                    with open('/home/repusight/data/' + filename, 'a') as f:
                        dtaFrm.to_csv(f, sep='|', encoding='utf-8', index=False, header=True)
                    print("1-Crawled")
                    return "Crawled"
                else:
                    driver.close()
                    print("2-Already Updated !!")
                    return "Already Updated !!"
            Rname = rev.find_element_by_tag_name("h4").text
            comment = rev.find_element_by_class_name("review_item_review_content").text
            comment.replace("눇", "")
            Rimg = rev.find_element_by_class_name("avatar-mask").get_attribute('src')
            Rating = rev.find_element_by_class_name("review-score-badge").text
            Rating = float(Rating)/2
            data.append(
                {"Name": hotelName, "Place": hotelPlace, "Date": date, "Rname": Rname,
                 "Rimg": Rimg, "Comment": comment, "ReviewID": "",
                 "Rating": Rating, "Channel": filter[0]["source"], "icon": "/static/images/Booking.png",
                 "Replied": "R", "Logo": filter[0]["Logo"], "URL": filter[0]["revertURL"],
                 "City": filter[0]["City"], "State": filter[0]["State"], "Country": filter[0]["Country"]})
        if driver.find_elements_by_id("review_next_page_link"):
            element = driver.find_element_by_id("review_next_page_link")
            driver.execute_script("arguments[0].click();", element)
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


def bookingClient(filter):
    try:
        # chromedriver = "/Documents/chromedriver"
        # os.environ["webdriver.chrome.driver"] = chromedriver
        # driver = webdriver.Chrome(executable_path=r"/home/repusight/Documents/chromedriver")
        driver = webdriver.Chrome()
        loginDetails = login_credentials(filter)
        filter[0]["url1"] = "https://admin.booking.com/hotel/hoteladmin/extranet_ng/manage/reviews.html"
        # filter[0]["url1"] = loginDetails[0]['ChannelUrl']
        driver.get(filter[0]["url1"])
        time.sleep(8)
        driver.maximize_window()

        hotelName = filter[0]["propertyName"]
        hotelPlace = filter[0]["Place"]

        loginId = loginDetails[0]['UserId']
        loginPassword = loginDetails[0]['Password']

        username = driver.find_element_by_id("loginname")
        password = driver.find_element_by_id("password")

        username.send_keys(loginId)
        password.send_keys(loginPassword)
        time.sleep(2)
        if driver.find_elements_by_xpath("//*[@id='wrap']/div[1]/div/section/div/section[1]/div/div/div[1]/form/button"):
            driver.find_element_by_xpath("//*[@id='wrap']/div[1]/div/section/div/section[1]/div/div/div[1]/form/button").click()
        else:
            driver.find_element_by_xpath("//*[ @ id = 'wrap']/div[1]/div/section/div/section[1]/div/div/div/div/form/button").click()
        time.sleep(5)
        no_of_pages = int(
            driver.find_element_by_xpath("//*[@id='content']/div/div[3]/div[1]/div/div[1]/ul").get_attribute(
                "data-page-size"))
        data=[]
        for page in range(0,no_of_pages):
            mainDiv = driver.find_element_by_class_name("reviews-list")
            allReviews = mainDiv.find_elements_by_class_name("review-block-body")
            for review in allReviews:
                try:
                    if review.find_element_by_class_name("review-date").text != "":
                        reviewDate = review.find_element_by_class_name("review-date").text
                        pattern = '%Y-%m-%d'
                        reviewDate = int(time.mktime(time.strptime(reviewDate, pattern)))
                    else:
                        reviewDate = None
                    if filter[0]["lastCrawl"] != "" and reviewDate != None and reviewDate <= int(filter[0]["lastCrawl"]):
                        if data:
                            dtaFrm = pd.DataFrame(data)
                            driver.close()
                            if not dtaFrm.empty:
                                app.config["PROPERTY_COLLECTION"].update({"_id": filter[0]["_id"]},
                                                                         {"$set": {"lastCrawl": round(time.time())}})
                            filename = (
                                str(filter[0]["propertyName"]) + "_" + str(filter[0]["Place"]) + "_" + str(
                                    filter[0]["source"]) + "_" + str(
                                    time.strftime("%d-%m-%Y")) + ".csv").replace(" ", "").replace("'", "")
                            with open('/home/repusight/data/' + filename, 'a') as f:
                                dtaFrm.to_csv(f, sep='|', encoding='utf-8', index=False, header=True)
                            print("1-Crawled")
                            return "Crawled"
                        else:
                            driver.close()
                            print("2-Already Updated !!")
                            return "Already Updated !!"
                    if review.find_element_by_class_name("review-id").text != '':
                        reviewId = int(review.find_element_by_class_name("review-id").text)
                    else:
                        reviewId = None
                    reviewRating = float(review.find_element_by_class_name("review-score").text)
                    reviewRating = round((reviewRating*5)/10,1)
                    Rname = review.find_element_by_class_name("review-guest-name").text
                    Rimg = filter[0]["Logo"]
                    if review.find_elements_by_class_name("review-block-content"):
                        comment = review.find_element_by_class_name("review-block-content").text
                    else:
                        comment = "No Comment"
                    if review.find_elements_by_link_text("View your response"):
                        Replied = "R1"
                    elif review.find_elements_by_link_text("View your approved response"):
                        Replied = "R1"
                    else:
                        Replied = "R0"
                    data.append(
                        {"Name": hotelName, "Place": hotelPlace, "Date": reviewDate, "Rname": Rname,
                         "Rimg": Rimg, "Comment": comment, "ReviewID": reviewId,
                         "Rating": reviewRating, "Channel": filter[0]["source"],
                         "icon": "/static/images/Booking.png",
                         "Replied": Replied, "Logo": filter[0]["Logo"], "URL": filter[0]["revertURL"],
                         "City": filter[0]["City"], "State": filter[0]["State"], "Country": filter[0]["Country"]})
                except Exception as e:
                    print(e)
                    pass
            driver.find_element_by_link_text("Next page »").click()
            time.sleep(4)
        print("3-Crawled")
        return "Crawled"
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
    print("4-Crawled")
    return "Crawled"
