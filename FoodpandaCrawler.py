import time, requests
import pandas as pd
from bs4 import BeautifulSoup
from app import app


def foodpanda(filter):
    try:
        html = requests.get(filter[0]["url1"]).text.encode('utf-8')
        soup = BeautifulSoup(html, 'lxml')
        data = []
        restaurantName = filter[0]["propertyName"]
        restaurantPlace = filter[0]["Place"]
        soup = soup.find("div", id="reviews")
        soup = soup.find("ul", class_="reviews")
        allreviews = soup.find_all("li", class_="reviews__review")
        for r in allreviews:
            rdate = r.find("span", class_="reviews__review__date__date")['content']
            pattern = '%Y-%m-%d'
            rdate = int(time.mktime(time.strptime(rdate, pattern)))
            if filter[0]["lastCrawl"] != "" and rdate <= int(filter[0]["lastCrawl"]):
                if data:
                    dtaFrm = pd.DataFrame(data)
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
                    print("2-Already Updated !!")
                    return "Already Updated !!"
            rname = r.find("span", class_="reviews__review__date__author").getText()
            rname = ' '.join([segment for segment in rname.split()])
            rname = rname[3:]
            rating = r.find("span", class_="rating-score")['content']
            try:
                if r.find("p", class_="reviews__review__review__title").getText():
                    reviewtitle = r.find("p", class_="reviews__review__review__title").getText()
                    reviewtitle = ' '.join([segment for segment in reviewtitle.split()])
                    if reviewtitle == "":
                        reviewtitle = None
                else:
                    reviewtitle = None
            except:
                reviewtitle = None
            try:
                if r.find("p", class_="reviews__review__review__comment").getText():
                    reviewcontent = r.find("p", class_="reviews__review__review__comment").getText()
                    reviewcontent = ' '.join([segment for segment in reviewcontent.split()])
                    if reviewcontent == "":
                        reviewcontent = None
                else:
                    reviewcontent = None
            except:
                reviewcontent = None
            if reviewtitle is None and reviewcontent is None:
                comment = "No Comment"
            elif reviewtitle is None and reviewcontent is not None:
                comment = reviewcontent
            elif reviewcontent is None and reviewtitle is not None:
                comment = reviewtitle
            elif reviewcontent is not None and reviewtitle is not None:
                comment = reviewtitle + " " + reviewcontent
            else:
                comment = "No Comment"
            data.append(
                {"Name": restaurantName, "Place": restaurantPlace, "Date": rdate, "Rname": rname,
                 "Rimg": filter[0]["Logo"], "Comment": comment, "ReviewID": "",
                 "Rating": rating, "Channel": filter[0]["source"], "icon": "/static/images/foodpanda_logo.jpg",
                 "Replied": "R2", "Logo": filter[0]["Logo"], "URL": filter[0]["revertURL"],
                 "City": filter[0]["City"], "State": filter[0]["State"], "Country": filter[0]["Country"]})
    except Exception as e:
        print(e)
        return "Something went wrong !!"
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
