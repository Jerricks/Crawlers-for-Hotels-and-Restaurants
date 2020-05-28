from app import app, lm
from flask import request, redirect, render_template, url_for, session
from flask_login import login_user, logout_user, login_required
from .forms import LoginForm
from .user import User
import json
import datetime, time
from htmlmin.minify import html_minify
from bson.objectid import ObjectId
from .model_email import send_mail, send_pdf_mail
from .model_report import reportSummary, create_pdf, create_pdf_inst
from .model_reply import maindef
from .TripAdvisorCrawler import tripadvisor
from .MakeMyTripCrawler import makemytrip
from .GoibbiboCrawler import goibibo
from .BookingCrawler import booking, bookingClient
from .ExpediaCrawler import expedia
from .GoogleCrawler import googleReview
from .HolidayIqCrawler import holidayIQClient, holidayIQ
from .ZomatoCrawler import zomato
from .EveningFlavorCrawler import eveningFlavor
from .AgodaCrawler import agoda
from .DineoutCrawler import dineOut
from .MouthshutCrawler import mouthshut
from .BurrpCrawler import burrp
from .FoodpandaCrawler import foodpanda
from .HotelClassifier import hotelClassifier
from .RestaurantClassifier import restaurantClassifier
from .HotelsCrawler import hotels

tech_recepients = ["niki.upadhyay@repusight.com"]


@app.route('/')
def home():
    return redirect(url_for("login"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = ""
    if request.method == 'POST' and form.validate_on_submit():
        user = app.config['REGISTEREDUSERS_COLLECTION'].find_one({"_id": form.username.data})
        if user and User.validate_login(user['password'], form.password.data) and user[u'status'] == True:
            user_obj = User(user['_id'])
            login_user(user_obj)
            session['logged_in'] = True
            session['user'] = user
            print("Logged in successfully!")
            if user['role'] == 'adminCrawler':
                return redirect(request.args.get("next") or url_for("crawler"))
        else:
            error = "Wrong username or password!"
    return html_minify(render_template('login.html', title='login', form=form, error=error))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    logout_user()
    return redirect(url_for('login'))


@lm.user_loader
def load_user(username):
    u = app.config['REGISTEREDUSERS_COLLECTION'].find_one({"_id": username})
    if not u:
        return None
    return User(u['_id'])


@app.route('/user', methods=["POST"])
def user():
    user_obj = session.get('user', None)
    return json.dumps(user_obj)


@app.route("/respond", methods=["POST"])
@login_required
def respond():
    user_obj = session.get('user', None)
    try:
        if request.method == 'POST':
            filter = request.get_json()
            reviewID = filter["reviewId"]
            mesage = filter["message"]
            channel = filter["channel"]
            rname = filter["rname"]
            name = filter["hotel"]
            place = filter["place"]
            rdate = filter["rdate"]
            objectId = filter["oid"]
            repliedDate = None
            city = "Bangalore"
            try:
                app.config["REPLIES_COLLECTION"].insert_one(
                    {"Source": channel, "CommentId": objectId, "PropertyName": name, "PropertyLocation": place,
                     "ReviewerName": rname, "ReplyText": mesage, "CommentDate": rdate, "reviewID": reviewID,
                     "RepliedStatus": repliedDate, "city": city})
                if user_obj['propType'] == 'Hotel':
                    app.config["HOTEL_COLLECTION"].update({"_id": ObjectId(str(objectId))}, {'$set': {"Replied": 3}})
                elif user_obj['propType'] == 'Restaurant':
                    app.config["RESTAURANT_COLLECTION"].update({"_id": ObjectId(str(objectId))},
                                                               {'$set': {"Replied": 3}})
                status = "Reply in Process !!"
            except (Exception) as e:
                print(e)
                status = "Something went wrong! Please try again later."
            return json.dumps({'msg': status})
    except Exception as e:
        print(e)
        status = "Something went wrong! Please try again later."
        user_obj = session.get('user', None)
        name = user_obj['hotel']
        place = user_obj['Place']
        status = "Something went wrong! Please try again later."
        recipients = tech_recepients
        esubject = "Error while responding to review on " + datetime.datetime.now().strftime("%d %b, %Y %I:%M:%S %p")
        ebody = "For " + name + ", " + place + "\nSome error has occured: \n" + str(e)
        ebody = ebody + "\n\n\nRepusight Support."
        send_mail(recipients, esubject, ebody)
        return json.dumps({'msg': status})


@app.route('/crawler')
@login_required
def crawler():
    return render_template('crawler.html')


@app.route("/propertyData", methods=["GET", "POST"])
@login_required
def propertyData():
    try:
        property_Data = list(app.config['PROPERTY_COLLECTION'].find({"Status": "Active"}))
        propertyList = list(set([x["propertyName"] + "," + x["Place"] for x in property_Data]))
        property_Hotel = list(
            app.config['PROPERTY_COLLECTION'].find({"Status": "Active", "For": "Hotel", "type": "Customer"}))
        property_Restaurant = list(
            app.config['PROPERTY_COLLECTION'].find({"Status": "Active", "For": "Restaurant", "type": "Customer"}))
        return json.dumps({"property_Data": property_Data, "propertyList": propertyList,
                           "property_Hotel": property_Hotel, "property_Restaurant": property_Restaurant})
    except Exception as e:
        print(e)
        return json.dumps({"property_Data": [], "propertyList": [], "property_Hotel": [], "property_Restaurant": []})


@app.route("/runcrawler", methods=["POST"])
@login_required
def runcrawler():
    if request.method == 'POST':
        filter = request.get_json()
        if filter is not None:
            dict = {}
            try:
                prop = filter["property"]
                propName = prop.split(",")[0]
                propLocation = prop.split(",")[1]
                cData = list(app.config['PROPERTY_COLLECTION'].find(
                    {"source": filter["source"], "propertyName": propName, "Place": propLocation}))
                if filter["source"] == "TripAdvisor":
                    status = tripadvisor(cData)
                    dict["status"] = status
                elif filter["source"] == "MakeMyTrip":
                    status = makemytrip(cData)
                    dict["status"] = status
                elif filter["source"] == "Goibibo":
                    status = goibibo(cData)
                    dict["status"] = status
                elif filter["source"] == "Booking":
                    if cData[0]["type"] == "Customer":
                        status = bookingClient(cData)
                    else:
                        status = booking(cData)
                    dict["status"] = status
                elif filter["source"] == "Expedia":
                    status = expedia(cData)
                    dict["status"] = status
                elif filter["source"] == "GoogleReview":
                    status = googleReview(cData)
                    dict["status"] = status
                elif filter["source"] == "HolidayIQ":
                    if cData[0]["type"] == "Customer":
                        status = holidayIQClient(cData)
                    else:
                        status = holidayIQ(cData)
                    dict["status"] = status
                elif filter["source"] == "Agoda":
                    status = agoda(cData)
                    dict["status"] = status
                elif filter["source"] == "Zomato":
                    status = zomato(cData)
                    dict["status"] = status
                elif filter["source"] == "EveningFlavors":
                    status = eveningFlavor(cData)
                    dict["status"] = status
                elif filter["source"] == "Dineout":
                    status = dineOut(cData)
                    dict["status"] = status
                elif filter["source"] == "Mouthshut":
                    status = mouthshut(cData)
                    dict["status"] = status
                elif filter["source"] == "Burrp":
                    status = burrp(cData)
                    dict["status"] = status
                elif filter["source"] == "Foodpanda":
                    status = foodpanda(cData)
                    dict["status"] = status
                elif filter["source"] == "Hotels":
                    status = hotels(cData)
                    dict["status"] = status
            except Exception as e:
                print(e)
                dict["status"] = "Something went wrong! Please try again later."
    return json.dumps(dict)


@app.route("/runclassifier", methods=["POST"])
@login_required
def runclassifier():
    status = "It is not POST Request"
    dict = {}
    if request.method == 'POST':
        filter = request.get_json()
        if filter["classifierType"] == "Hotel":
            status = hotelClassifier(filter)
        else:
            status = restaurantClassifier(filter)
    dict["status"] = status
    return json.dumps(dict)


@app.route('/report')
@login_required
def report():
    return html_minify(render_template('report.html'))


@app.route('/reply')
@login_required
def reply():
    return render_template('reply.html')


@app.route('/reportData', methods=['GET', 'POST'])
@login_required
def reportData():
    reportdata = []
    if request.method == "POST":
        filter = request.get_json()
        if filter is not None:
            ptype = filter['type']
            name = filter['name']
            place = filter['place']
            if filter['startdt'] != "" and filter['enddt'] != "":
                startd = int(time.mktime(datetime.datetime.strptime(filter['startdt'], '%d/%m/%Y').timetuple()))
                endd = int(time.mktime(datetime.datetime.strptime(filter['enddt'], '%d/%m/%Y').timetuple()))

                start_date_stripped = filter['startdt']
                start_date_stripped = time.strptime(start_date_stripped, "%d/%m/%Y")
                start_date_stripped = (time.strftime("%d %b %Y", start_date_stripped))

                end_date_stripped = filter['enddt']
                end_date_stripped = time.strptime(end_date_stripped, "%d/%m/%Y")
                end_date_stripped = (time.strftime("%d %b %Y", end_date_stripped))

            else:
                sevendays = datetime.date.today() - datetime.timedelta(7)
                startd = int(sevendays.strftime("%s"))
                endd = int(datetime.date.today().strftime("%s"))
            reportdata = reportSummary(ptype, name, place, startd, endd)
            reportdata['subject'] = 'Summary report from {0} to {1}'.format(start_date_stripped, end_date_stripped)
            session['result_data'] = reportdata
            session['name'] = reportdata['property_info']['Name']
    return json.dumps({"reportdata": reportdata})


@app.route('/generate_pdf')
@login_required
def send_pdf():
    all_data = session.get('result_data', None)
    name = session.get('name', None)

    if all_data is None:
        return redirect(url_for('report'))

    rendered = html_minify(render_template('pdfreport.html', property_info=all_data['property_info'],
                               subject=all_data['subject'], totalReview=all_data['allReviews'],
                               averageRating=all_data['avg_rating'], percentageCSI=all_data['CSI'],
                               managementResponse=all_data['response_freq'], dept_index=all_data['dept_index_info'],
                               otaInfo=all_data['Ota_info'], status=all_data['csi_status']))

    return create_pdf(rendered, name)


@app.route("/send_mail_pdf", methods=['GET', 'POST'])
@login_required
def send_mail_pdf():
    if request.method == 'GET':
        all_data = session.get('result_data', None)
        name = session.get('name', None)

        if all_data is None:
            return redirect(url_for('report'))

        rendered = html_minify(render_template('pdfreport.html', property_info=all_data['property_info'],
                                   subject=all_data['subject'], totalReview=all_data['allReviews'],
                                   averageRating=all_data['avg_rating'], percentageCSI=all_data['CSI'],
                                   managementResponse=all_data['response_freq'], dept_index=all_data['dept_index_info'],
                                   otaInfo=all_data['Ota_info'], status=all_data['csi_status']))

        pdf = create_pdf_inst(rendered)

        status_dict = send_pdf_mail(attachment=pdf, pdf_name=name,
                                    recipients=["sanket.mokashi@repusight.com", "jerricks.s@repusight.com"],
                                    cc=['niki.upadhyay@repusight.com'], subject='Periodic analysis', name=name)

        return json.dumps(status_dict)

    else:
        app.logger.error('GET response expected')
        return json.dumps({'error': '501'})


@app.route('/responseNow', methods=['GET', 'POST'])
@login_required
def responseNow():
    try:
        maindef()
        return json.dumps({'Status': 'Success'})
    except Exception as e:
        print(e)
        return json.dumps({'Status': 'Error'})
