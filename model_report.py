from app import app
import math
from flask_weasyprint import render_pdf, HTML

topicHotel = ['Food', 'Service', 'Value', 'Ambience', 'Cleanliness', 'Amenities', 'Hospitality', 'Location',
              'Front-Desk', 'Room']

topicRestaurant = ['Taste', 'Variety', 'Drinks', 'Service', 'Value', 'Hygiene', 'Ambience', 'Hospitality', 'Comforts',
                   'Entertainment']


def check_collection(propType):
    if propType == 'Hotel':
        connect = app.config['HOTEL_COLLECTION']
    elif propType == 'Restaurant':
        connect = app.config['RESTAURANT_COLLECTION']
    return connect


def getPropDetail(pname, pplace):
    if pplace == "--All--":
        data = list(app.config['PROPERTY_COLLECTION'].aggregate([{"$match": {"propertyName": pname}}, {
            "$group": {"_id": {"propertyName": pname, "City": "$City", "State": "$State",
                               "Country": "$Country"}}}]))
        propdetail = data[0]['_id']['City'] + ", " + data[0]['_id']['State'] + ", " + data[0]['_id']['Country']
    else:
        data = list(app.config['PROPERTY_COLLECTION'].aggregate([{"$match": {"propertyName": pname, "Place": pplace}}, {
            "$group": {"_id": {"propertyName": pname, "Place": pplace, "City": "$City", "State": "$State",
                               "Country": "$Country"}}}]))
        propdetail = data[0]['_id']['Place'] + ", " + data[0]['_id']['City'] + ", " + data[0]['_id']['State'] + ", " + \
                     data[0]['_id']['Country']
    return propdetail


def getCity(pname, pplace):
    if pplace == "--All--":
        data = list(app.config['PROPERTY_COLLECTION'].aggregate([{"$match": {"propertyName": pname}}, {
            "$group": {"_id": {"propertyName": pname, "City": "$City", "State": "$State",
                               "Country": "$Country"}}}]))
    else:
        data = list(app.config['PROPERTY_COLLECTION'].aggregate([{"$match": {"propertyName": pname, "Place": pplace}}, {
            "$group": {"_id": {"propertyName": pname, "Place": pplace, "City": "$City", "State": "$State",
                               "Country": "$Country"}}}]))
    cityname = data[0]['_id']['City']
    return cityname


def totalReviews(collection, pname, pplace, startdt, enddt):
    name = pname
    city = getCity(pname, pplace)
    place = pplace
    start = startdt
    end = enddt
    if place == "--All--":
        total_reviews = collection.find({'Name': name, 'City': city, 'Date': {'$gte': start, '$lt': end}}).count()

        total_reviews_pos = collection.find({'Name': name, 'City': city, 'Sentiment': 1,
                                             'Date': {'$gte': start, '$lt': end}}).count()
        total_reviews_Neg = collection.find({'Name': name, 'City': city, 'Sentiment': 2,
                                             'Date': {'$gte': start, '$lt': end}}).count()
        total_reviews_other = collection.find(
            {'Name': name, 'City': city, '$or': [{'Sentiment': 0}, {'Sentiment': 3}],
             'Date': {'$gte': start, '$lt': end}}).count()
        neutral_reviews = collection.find({'Name': name, 'City': city,
                                           'Date': {'$gte': start, '$lt': end},
                                           }).count()
    else:
        total_reviews = collection.find({'Name': name, 'Place': place, 'Date': {'$gte': start, '$lt': end}}).count()

        total_reviews_pos = collection.find({'Name': name, 'Place': place, 'City': city, 'Sentiment': 1,
                                             'Date': {'$gte': start, '$lt': end}}).count()
        total_reviews_Neg = collection.find({'Name': name, 'Place': place, 'City': city, 'Sentiment': 2,
                                             'Date': {'$gte': start, '$lt': end}}).count()

        total_reviews_other = collection.find(
            {'Name': name, 'Place': place, 'City': city, '$or': [{'Sentiment': 0}, {'Sentiment': 3}],
             'Date': {'$gte': start, '$lt': end}}).count()
        neutral_reviews = collection.find({'Name': name, 'Place': place,
                                           'Date': {'$gte': start, '$lt': end}
                                           }).count()
    if total_reviews == 0:
        CSI = 0
    else:
        CSI = (
                  2 * total_reviews - (
                      neutral_reviews * 0.5) - total_reviews_Neg) * 100.0
        CSI /= 2 * total_reviews

    if total_reviews != 0:
        neg_per = math.ceil((total_reviews_Neg / total_reviews) * 100)
        pos_per = math.ceil((total_reviews_pos / total_reviews) * 100)
    else:
        neg_per = 0
        pos_per = 0

    data = {"total_reviews": total_reviews, "positive_reviews": total_reviews_pos,
            "negative_reviews": total_reviews_Neg, 'other_reviews': total_reviews_other, "CSI": CSI,
            "pos_per": pos_per, "neg_per": neg_per}
    return data


def generate_csi_status(csi):
    if csi in range(0, 50):
        return 'Poor'

    elif csi in range(50, 60):
        return 'Below Average'

    elif csi in range(60, 70):
        return 'Average'

    elif csi in range(70, 80):
        return 'Good'

    elif csi in range(80, 90):
        return 'Excellent'

    elif csi in range(90, 100):
        return 'Outstanding'


def avgRating(collection, pname, pplace, startdt, enddt):
    name = pname
    city = getCity(pname, pplace)
    place = pplace
    start = startdt
    end = enddt
    if place == "--All--":
        data = list(
            collection.aggregate([{"$match": {"Name": name, "City": city, 'Date': {'$gte': start, '$lt': end}}},
                                  {"$group": {"_id": "null", "avg_rating": {"$avg": "$Rating"}}}]))
    else:
        data = list(
            collection.aggregate([{"$match": {"Name": name, "Place": place, 'Date': {'$gte': start, '$lt': end}}},
                                  {"$group": {"_id": "null", "avg_rating": {"$avg": "$Rating"}}}]))
    try:
        data = round(data[0]['avg_rating'], 2)
    except:
        data = 0
    return data


def summaryOTA(collection, pname, pplace, startdt, enddt):
    name = pname
    city = getCity(pname, pplace)
    place = pplace
    start = startdt
    end = enddt
    data = []
    if place == "--All--":
        al = list(collection.aggregate(
            [{"$match": {"Name": name, "City": city, 'Date': {'$gte': start, '$lt': end}}},
             {"$group": {"_id": {"Name": name, "City": city, "Channel": "$Channel", "icon": "$icon"}}}]))
        for ele in al:
            total_reviews = collection.find({'Name': name, 'City': city, "Channel": ele["_id"]["Channel"],
                                             'Date': {'$gte': start, '$lt': end}}).count()
            avg_rating_list = list(collection.aggregate([{"$match": {"Name": name, "City": city,
                                                                     "Channel": ele["_id"]["Channel"],
                                                                     'Date': {'$gte': start, '$lt': end}}}, {
                                                             "$group": {"_id": "null",
                                                                        "avg_rating": {"$avg": "$Rating"}}}]))
            if avg_rating_list != []:
                avg_rating = round(avg_rating_list[0]['avg_rating'], 2)
            else:
                avg_rating = 0
            data.append({"Channel": ele["_id"]["Channel"], "icon": ele["_id"]["icon"], "total_reviews": total_reviews,
                         "avg_rating": avg_rating})
    else:
        al = list(collection.aggregate([{"$match": {"Name": name, "Place": place, 'Date': {'$gte': start, '$lt': end}}},
                                        {"$group": {"_id": {"Name": name, "Place": place, "Channel": "$Channel",
                                                            "icon": "$icon"}}}]))
        for ele in al:
            total_reviews = collection.find({'Name': name, 'Place': place, "Channel": ele["_id"]["Channel"],
                                             'Date': {'$gte': start, '$lt': end}}).count()
            avg_rating_list = list(collection.aggregate([{"$match": {"Name": name, "Place": place,
                                                                     "Channel": ele["_id"]["Channel"],
                                                                     'Date': {'$gte': start, '$lt': end}}}, {
                                                             "$group": {"_id": "null",
                                                                        "avg_rating": {"$avg": "$Rating"}}}]))
            if avg_rating_list:
                avg_rating = round(avg_rating_list[0]['avg_rating'], 2)
            else:
                avg_rating = 0
            data.append({"Channel": ele["_id"]["Channel"], "icon": ele["_id"]["icon"], "total_reviews": total_reviews,
                         "avg_rating": avg_rating})
    return data


def deptIndex(collection, pname, pplace, startdt, enddt, ptype):
    name = pname
    city = getCity(pname, pplace)
    start = startdt
    end = enddt
    place = pplace
    data = list()
    if ptype == 'Hotel':
        TopicCategories = topicHotel
    elif ptype == 'Restaurant':
        TopicCategories = topicRestaurant
    if place == "--All--":
        for x in TopicCategories:
            total_reviews_present_month = collection.find({'Name': name, 'City': city,
                                                           'Date': {'$gte': start, '$lt': end},
                                                           x: {'$ne': 3}}).count()
            postive_reviews_present_month = collection.find({'Name': name, 'City': city,
                                                             'Date': {'$gte': start, '$lt': end},
                                                             x: 1}).count()
            negative_reviews_present_month = collection.find({'Name': name, 'City': city,
                                                              'Date': {'$gte': start, '$lt': end},
                                                              x: 2}).count()
            neutral_reviews_present_month = collection.find({'Name': name, 'City': city,
                                                             'Date': {'$gte': start, '$lt': end},
                                                             x: 0}).count()
            total_reviews_other_present_month = collection.find(
                {'Name': name, 'City': city, '$or': [{x: 0}, {x: 3}],
                 'Date': {'$gte': start, '$lt': end}}).count()
            if total_reviews_present_month == 0:
                CSI_present_month = 0
                change = 100.0
            else:
                CSI_present_month = (
                                        2 * total_reviews_present_month - (
                                            neutral_reviews_present_month * 0.5) - negative_reviews_present_month) * 100.0
                CSI_present_month /= 2 * total_reviews_present_month

                total_reviews_last_month = collection.find({'Name': name, 'City': city,
                                                            'Date': {'$gte': 2 * start - end, '$lt': start},
                                                            x: {'$ne': 3}}).count()
                postive_reviews_last_month = collection.find({'Name': name, 'City': city,
                                                              'Date': {'$gte': 2 * start - end,
                                                                       '$lt': start}, x: 1}).count()
                negative_reviews_last_month = collection.find({'Name': name, 'City': city,
                                                               'Date': {'$gte': 2 * start - end,
                                                                        '$lt': start}, x: 2}).count()
                neutral_reviews_last_month = collection.find({'Name': name, 'City': city,
                                                              'Date': {'$gte': 2 * start - end,
                                                                       '$lt': start}, x: 0}).count()

                if total_reviews_last_month == 0:
                    CSI_last_month = 0

                else:
                    CSI_last_month = (2 * total_reviews_last_month - (
                        neutral_reviews_last_month * 0.5) - negative_reviews_last_month) * 100.0
                    CSI_last_month /= 2 * total_reviews_last_month

                if CSI_last_month != 0.0:
                    change = (CSI_present_month - CSI_last_month) * 100.0
                    change /= CSI_last_month

                else:
                    change = 100.0

                if change < 0:
                    change = -(change)
                    csiUpDown = "fa-caret-down"
                    csiClass = "text-red"

                elif change == 0 or change > 0:
                    csiUpDown = "fa-caret-up"
                    csiClass = "text-green"

            data.append({"topic": x, "CSI": round(CSI_present_month, 2),
                         "mention": total_reviews_present_month, "positive": postive_reviews_present_month,
                         "change": round(change, 2),
                         "Negative": negative_reviews_present_month,
                         "Others": total_reviews_other_present_month, "csiUpDown": csiUpDown, "csiClass": csiClass})
    else:
        for x in TopicCategories:
            total_reviews_present_month = collection.find({'Name': name, 'Place': place, 'City': city,
                                                           'Date': {'$gte': start, '$lt': end},
                                                           x: {'$ne': 3}}).count()
            postive_reviews_present_month = collection.find({'Name': name, 'Place': place, 'City': city,
                                                             'Date': {'$gte': start, '$lt': end},
                                                             x: 1}).count()
            negative_reviews_present_month = collection.find({'Name': name, 'Place': place, 'City': city,
                                                              'Date': {'$gte': start, '$lt': end},
                                                              x: 2}).count()
            neutral_reviews_present_month = collection.find({'Name': name, 'Place': place, 'City': city,
                                                             'Date': {'$gte': start, '$lt': end},
                                                             x: 0}).count()
            total_reviews_other_present_month = collection.find(
                {'Name': name, 'Place': place, 'City': city, '$or': [{x: 0}, {x: 3}],
                 'Date': {'$gte': start, '$lt': end}}).count()
            if total_reviews_present_month == 0:
                CSI_present_month = 0
                change = 0
            else:
                CSI_present_month = (
                                        2 * total_reviews_present_month - (
                                            neutral_reviews_present_month * 0.5) - negative_reviews_present_month) * 100.0
                CSI_present_month /= 2 * total_reviews_present_month

            total_reviews_last_month = collection.find({'Name': name, 'Place': place,
                                                        'Date': {'$gte': 2 * start - end, '$lt': start},
                                                        x: {'$ne': 3}}).count()
            postive_reviews_last_month = collection.find({'Name': name, 'Place': place,
                                                          'Date': {'$gte': 2 * start - end,
                                                                   '$lt': start}, x: 1}).count()
            negative_reviews_last_month = collection.find({'Name': name, 'Place': place,
                                                           'Date': {'$gte': 2 * start - end,
                                                                    '$lt': start}, x: 2}).count()
            neutral_reviews_last_month = collection.find({'Name': name, 'Place': place,
                                                          'Date': {'$gte': 2 * start - end,
                                                                   '$lt': start}, x: 0}).count()

            if total_reviews_last_month == 0:
                CSI_last_month = 0

            else:
                CSI_last_month = (2 * total_reviews_last_month - (
                    neutral_reviews_last_month * 0.5) - negative_reviews_last_month) * 100.0
                CSI_last_month /= 2 * total_reviews_last_month

            if CSI_last_month != 0.0:
                change = (CSI_present_month - CSI_last_month) * 100.0
                change /= CSI_last_month

            else:
                change = 100.0

            if change < 0:
                change = -change
                csiUpDown = "fa-caret-down"
                csiClass = "text-red"

            elif change == 0 or change > 0:
                csiUpDown = "fa-caret-up"
                csiClass = "text-green"

            data.append({"topic": x, "CSI": round(CSI_present_month, 2),
                         "mention": total_reviews_present_month, "positive": postive_reviews_present_month,
                         "change": round(change, 2),
                         "Negative": negative_reviews_present_month,
                         "Others": total_reviews_other_present_month, "csiUpDown": csiUpDown, "csiClass": csiClass})
    return data


def mgmt_response(collection, pname, pplace, startdt, enddt):
    name = pname
    city = getCity(pname, pplace)
    place = pplace
    start = startdt
    end = enddt
    if place == "--All--":
        total_reviews = collection.find(
            {'Name': name, 'City': city}).count()

        repliednone = collection.find(
            {'Name': name, 'City': city, "Replied": "R", 'Date': {'$gte': start, '$lt': end}}).count()
        repliednone1 = collection.find(
            {'Name': name, 'City': city, 'Date': {'$gte': start, '$lt': end}, "Replied": ""}).count()
        replied0 = collection.find(
            {'Name': name, 'City': city, 'Date': {'$gte': start, '$lt': end}, "Replied": "R0"}).count()
        replied1 = collection.find(
            {'Name': name, 'City': city, 'Date': {'$gte': start, '$lt': end}, "Replied": "R1"}).count()
        replied2 = collection.find(
            {'Name': name, 'City': city, 'Date': {'$gte': start, '$lt': end}, "Replied": "R2"}).count()

        if total_reviews == (repliednone + replied2 + repliednone1):
            mgtrespstr = "No"
        else:
            if total_reviews != 0:
                mgtresp = round((replied1 / total_reviews) * 100, 2)
                mgtrespstr = str(mgtresp) + "%"
            else:
                mgtrespstr = 'NIL'
        return mgtrespstr

    else:
        total_reviews = collection.find(
            {'Name': name, 'Place': place, 'Date': {'$gte': start, '$lt': end}, 'City': city}).count()

        repliednone = collection.find(
            {'Name': name, 'Place': place, 'City': city, 'Date': {'$gte': start, '$lt': end}, "Replied": "R"}).count()
        repliednone1 = collection.find(
            {'Name': name, 'Place': place, 'City': city, 'Date': {'$gte': start, '$lt': end}, "Replied": ""}).count()
        replied0 = collection.find(
            {'Name': name, 'Place': place, 'City': city, 'Date': {'$gte': start, '$lt': end}, "Replied": "R0"}).count()
        replied1 = collection.find(
            {'Name': name, 'Place': place, 'City': city, 'Date': {'$gte': start, '$lt': end}, "Replied": "R1"}).count()
        replied2 = collection.find(
            {'Name': name, 'Place': place, 'City': city, 'Date': {'$gte': start, '$lt': end}, "Replied": "R2"}).count()

        if total_reviews == (repliednone + replied2 + repliednone1):
            mgtrespstr = "Not Required"

        else:
            if total_reviews != 0:
                mgtresp = round((replied1 / total_reviews) * 100, 2)
                mgtrespstr = str(mgtresp) + "%"

            else:
                mgtrespstr = 'NIL'

        return mgtrespstr


def reportSummary(ptype, pname, pplace, startdt, enddt):
    collection = check_collection(ptype)
    location = getPropDetail(pname, pplace)
    allReviews = totalReviews(collection, pname, pplace, startdt, enddt)
    csi = round(int(allReviews['CSI']), 2)
    csi_status = generate_csi_status(csi)
    avg_rating = avgRating(collection, pname, pplace, startdt, enddt)
    dept_index_info = deptIndex(collection, pname, pplace, startdt, enddt, ptype)
    Ota_info = summaryOTA(collection, pname, pplace, startdt, enddt)
    response_freq = mgmt_response(collection, pname, pplace, startdt, enddt)

    del allReviews['CSI']

    dict = {"location": location, 'allReviews': allReviews, 'CSI': csi, 'csi_status': csi_status,
            'avg_rating': avg_rating, 'Ota_info': Ota_info, 'response_freq': response_freq,
            'dept_index_info': dept_index_info, "property_info":{"Name":pname, "Location": location}}
    return dict


def create_pdf(template_inst, name):
    return render_pdf(HTML(string=template_inst))


def create_pdf_inst(template):
    return HTML(string=template).write_pdf()