import time, os
from selenium import webdriver
import pandas as pd
from bs4 import BeautifulSoup
from app import app


def login_credentials(filter):
    name = filter[0]['propertyName']
    place = filter[0]['Place']
    city = filter[0]['City']
    channel = filter[0]['source']
    if name in ["Ammi's Biryani", "RICE BAR", "Sultan's Biryani"]:
        details = list(app.config["REPLYCREDENTIALS_COLLECTION"].find({'Name': name, 'City': city, 'Channel': channel}))
    else:
        details = app.config["REPLYCREDENTIALS_COLLECTION"].find(
            {'Name': name, 'Place': place, 'City': city, 'Channel': channel})
    return details


def holidayIQClient(filter):
    # chromedriver = "/Documents/chromedriver"
    # os.environ["webdriver.chrome.driver"] = chromedriver
    # driver = webdriver.Chrome(executable_path=r"/home/repusight/Documents/chromedriver")
    driver = webdriver.Chrome()
    loginDetails = login_credentials(filter)
    filter[0]["url1"] = loginDetails[0]['ChannelUrl']
    driver.get(filter[0]["url1"])
    time.sleep(8)
    driver.maximize_window()

    loginId = loginDetails[0]['UserId']
    loginPassword = loginDetails[0]['Password']

    username = driver.find_element_by_id("exampleInputEmail1")
    password = driver.find_element_by_id("exampleInputPassword1")

    username.send_keys(loginId)
    password.send_keys(loginPassword)

    driver.find_element_by_class_name("btn").click()

    hotelName = filter[0]["propertyName"]
    hotelPlace = filter[0]["Place"]
    pages = driver.find_element_by_class_name("pagination")
    noPages = pages.find_elements_by_tag_name("li")
    pagetxt = int(noPages[-2].text)
    data = []
    currentUrl = driver.current_url
    for number in range(1, pagetxt + 1):
        driver.get(currentUrl + "&page=" + str(number) + "#reviews")
        time.sleep(5)
        source = driver.page_source
        soup = BeautifulSoup(source, "html.parser")
        table = soup.find("table", id="reviewListTable")
        rows = table.find_all("tr", class_="review-row")
        for row in rows:
            try:
                tds = row.find_all("td")
                date = tds[0].getText()
                pattern = '%b %d, %Y'
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
                inputTag = tds[1].find_next("input")
                value = inputTag["value"]
                commentTag = soup.find("tr", id="collapse-" + str(value))
                comment = commentTag.find("div", class_="show").get_text()
                comment = comment.replace("Show (+)", "")
                rname = tds[3].getText()
                rname = rname[16:]
                rating = tds[4].getText()
                rating = rating.replace(" ", "")
                rating = round(float(float(rating) * 5) / 7, 1)
                approve = tds[6].getText()
                approve = approve.replace("\n", "")
                approve = approve.replace(" ", "")
                if approve == "Approved":
                    replied = "R1"
                else:
                    replied = "R0"
                rimg = filter[0]["Logo"]
                data.append(
                    {"Name": hotelName, "Place": hotelPlace, "Date": date, "Rname": rname,
                     "Rimg": rimg, "Comment": comment, "ReviewID": "",
                     "Rating": rating, "Channel": filter[0]["source"], "icon": "/static/images/logo-holidayiq.png",
                     "Replied": replied, "Logo": filter[0]["Logo"], "URL": filter[0]["revertURL"],
                     "City": filter[0]["City"], "State": filter[0]["State"], "Country": filter[0]["Country"]})
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
    return "Crawled"


def holidayIQ(filter):
    pattern = '%d %B %Y'
    dummy_img = 'https://c1.hiqcdn.com/photos/ph/Photos-dummy-profile-pic-gif-discovery-resources-images-57x54-1366206786.gif'
    # chromedriver = "/Documents/chromedriver"
    # os.environ["webdriver.chrome.driver"] = chromedriver
    # driver = webdriver.Chrome(executable_path=r"/home/repusight/Documents/chromedriver")
    driver = webdriver.Chrome()
    driver.get(filter[0]['url1'])
    driver.maximize_window()
    time.sleep(7)
    data = list()
    try:
        while 1:
            driver.find_element_by_id('loadMoreTextReview').click()
    except:
        pass
    soup = BeautifulSoup(driver.page_source, "lxml")
    driver.close()
    revs = soup.find('div', {'class': 'detail-review-by-hotel'})
    revs = revs.find('div', {'id': 'result-items'})
    revs = revs.find_all('div', {'itemprop': 'review'})
    for rev in revs:
        date = rev.find('meta', {'itemprop': 'datePublished'})['content'].replace(',', '')
        date = int(time.mktime(time.strptime(date, pattern)))
        if date > filter[0]['lastCrawl']:
            if type(rev.find('img', {'class': 'pull-right'})) == type(None):
                rname = rev.find('h4', {'class': 'media-heading'}).text
                comment = rev.find('p', {'itemprop': 'reviewBody'}).text
                rating = float(rev.find('span', {'class': 'dtl-rating-num'}).text.replace('/7', ''))
                rating = round(float(float(rating) * 5) / 7, 2)
                rimg = rev.find('img', {'class': 'media-object'})['src']

                if rimg == dummy_img:
                    rimg = filter[0]['Logo']

                data.append(
                    {"Name": filter[0]['propertyName'], "Place": filter[0]['Place'], "Date": int(round(date)),
                     "Rname": rname,
                     "Rimg": rimg, "Comment": comment, "ReviewID": "",
                     "Rating": rating, "Channel": filter[0]["source"], "icon": "/static/images/logo-holidayiq.png",
                     "Replied": 'R2', "Logo": filter[0]["Logo"], "URL": filter[0]["revertURL"],
                     "City": filter[0]["City"], "State": filter[0]["State"], "Country": filter[0]["Country"]})
        else:
            print("1-Already Updated !!")
            return "Already Updated !!"
    data_pd = pd.DataFrame(data)
    if not data_pd.empty:
        print(data_pd)
        app.config["PROPERTY_COLLECTION"].update({"_id": filter[0]["_id"]}, {"$set": {"lastCrawl": round(time.time())}})
        filename = (str(filter[0]["propertyName"]) + "_" + str(filter[0]["Place"]) + "_" + str(
            filter[0]["source"]) + "_" + str(time.strftime("%d-%m-%Y")) + ".csv").replace(" ", "").replace("'", "")
        with open('/home/repusight/data/' + filename, 'a') as f:
            data_pd.to_csv(f, sep='|', encoding='utf-8', index=False, header=True)
        print("2-Crawled")
        return "Crawled"
