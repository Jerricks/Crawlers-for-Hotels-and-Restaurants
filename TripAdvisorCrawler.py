import time, os
from selenium import webdriver
import pandas as pd
import math
from app import app


def tripadvisor(filter):
    # This crawler is made completely using selenium

    # chromedriver = "/Documents/chromedriver"   #getting the chrome instance
    # os.environ["webdriver.chrome.driver"] = chromedriver
    # driver = webdriver.Chrome(executable_path=r"/home/repusight/Documents/chromedriver")

    driver = webdriver.Chrome()

    driver.get(filter[0]["url1"] + filter[0]["url2"])  # getting the url and open page
    time.sleep(8)
    # Maximiazing Browser to window size

    driver.maximize_window()

    # get the total no. of reviews for the property. Find out the no. of reviews present on one page.
    # Dividing no. of reviews by no. of reviews on single page gives total no. of pages(count1 here).

    totalreviews = driver.find_element_by_xpath(
        "//*[@id='taplc_location_detail_header_hotels_0']/div[1]/span[1]/div/a/span").text
    totalreviews = int(totalreviews)
    count1 = math.ceil(int(totalreviews) / 5)
    data = []
    # get hotel name and place from filter (property data send as parameter)
    hotelName = filter[0]["propertyName"]
    place = filter[0]["Place"]

    flagCount = 0  # flagcount is used to loop pages on count of 5,10,15 and so on...
    # this for is to loop through pages
    for g in range(0, count1):
        try:
            driver.get(filter[0]["url1"] + str(flagCount * 5) + filter[0]["url2"])
            time.sleep(5)
            flagCount = flagCount + 1

            # This is to find any review contains read more
            more = driver.find_elements_by_css_selector(".taLnk.ulBlueLinks")
            if more:  # if contains click and it will open all read more on the page
                driver.execute_script("arguments[0].click();", more[0])
            # This for is to loop through reviews present on the page
            for reviewer in range(1, 6):
                reviewer = reviewer * 2 + 1  # Review element are present as odd pattern 3,5,7 and so on...
                try:
                    # getting the review using xpath
                    content = driver.find_element_by_xpath(
                        "//*[@id='taplc_location_reviews_list_hotels_0']/div[1]/div[" + str(reviewer) + "]")

                    reviewId = content.get_attribute("data-reviewid")  # Get review Id

                    # get geview date
                    if content.find_element_by_class_name('ratingDate').get_attribute(
                            'title') != "":  # check if date is present as '7 days ago'
                        date = content.find_element_by_class_name('ratingDate').get_attribute('title')
                    else:
                        date = content.find_element_by_class_name('ratingDate').text
                        date = date.replace('Reviewed ', '')
                    if date != '':
                        pattern = '%d %B %Y'
                        date = int(time.mktime(time.strptime(date, pattern)))  # convert date into epoch time

                    # check last crawled date and match with review. If matched make dataframe of currently filled data(list)
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

                    # Checks if the review is already replied or not
                    if content.find_elements_by_class_name("mgrRspnInline"):
                        Replied = "R1"
                    else:
                        Replied = "R0"

                    # Find comment
                    if content.find_element_by_class_name("entry").text != '':
                        comment = content.find_element_by_class_name("entry").text
                    else:
                        comment = "No Comment"

                    # Get the rating of the review
                    rati = content.find_element_by_class_name('rating')
                    rating = rati.find_element_by_tag_name('span').get_attribute('class')
                    rating = (int((rating.split("_"))[3])) / 10
                    rpic1 = content.find_element_by_class_name('avatar')
                    rpic = rpic1.find_element_by_tag_name("a")

                    # Get reviewer Image
                    reviewerImage = rpic.find_element_by_tag_name('img').get_attribute('src')

                    # Get Reviewer Name
                    rnam = content.find_element_by_class_name('username')
                    reviewerName = rnam.find_element_by_tag_name('span').text

                    # append all variables into data list
                    data.append(
                        {"Name": hotelName, "Place": place, "Date": date, "Rname": reviewerName,
                         "Rimg": reviewerImage, "Comment": comment, "ReviewID": reviewId,
                         "Rating": rating, "Channel": filter[0]["source"],
                         "icon": "/static/images/TripAdvisor_logo.png",
                         "Replied": Replied, "Logo": filter[0]["Logo"], "URL": filter[0]["revertURL"],
                         "City": filter[0]["City"], "State": filter[0]["State"], "Country": filter[0]["Country"]})
                except Exception as e:
                    app.logger.error(e)
                    print(e)
                    pass
        except (Exception) as e:
            print(e)
            app.logger.error(e)
            pass
    dtaFrm = pd.DataFrame(data)  # create a dataframe from data
    driver.close()  # Close Chrome Instance
#    if not dtaFrm.empty:
        # Update Last Crawled
#        app.config["PROPERTY_COLLECTION"].update({"_id": filter[0]["_id"]}, {"$set": {"lastCrawl": round(time.time())}})
    filename = (
        str(filter[0]["propertyName"]) + "_" + str(filter[0]["Place"]) + "_" + str(filter[0]["source"]) + "_" + str(
            time.strftime("%d-%m-%Y")) + ".csv").replace(" ", "").replace("'", "")
    with open('/home/repusight/data/' + filename, 'a') as f:
        # Save data frame as csv on given path
        dtaFrm.to_csv(f, sep='|', encoding='utf-8', index=False, header=True)
    print("3-Crawled")
    return "Crawled"
