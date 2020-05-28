#!/usr/bin/python
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import datetime
import math
from bson.objectid import ObjectId
from pyvirtualdisplay import Display
from pymongo import MongoClient
import logging

#logging.basicConfig(filename="replies.log", level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")

DB_NAME = 'proDB'
# ip = '127.0.0.1'
ip = '52.66.167.52'
port=27017
DATABASE = MongoClient(ip,port)[DB_NAME]

display = Display(visible=0,size=(1920, 1080))
display.start()

dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Chrome/56.0.2924.87 Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 (KHTML, like Gecko)")




def send_mail(recipients, eSubject, eBody):
    # mail = smtplib.SMTP("smtp.zoho.com",465)
    # mail.ehlo()
    # mail.starttls()
    # mail.login("support@repusight.com","repusight")
    # mail.sendmail("support@repusight.com",recipients,eBody)
    # mail.close()
    print(eSubject + " " + eBody)


def login_credentials(filter):
    name = filter['PropertyName']
    place = filter['PropertyLocation']
    city = filter['city']
    channel = filter['Source']
    if name in ["Ammi's Biryani", "RICE BAR", "Sultan's Biryani"]:
        details = list(DATABASE.replyLoginCredentials.find({'Name': name, 'City': city, 'Channel': channel}))
    else:
        details = DATABASE.replyLoginCredentials.find({'Name': name, 'Place': place, 'City': city, 'Channel': channel})
    return details


def replyTripadvisor(url,message,objectId,filter):
    try:
        # driver = webdriver.PhantomJS(desired_capabilities=dcap,service_args=['--ignore-ssl-errors=true'])
        #driver = webdriver.PhantomJS(executable_path=r"/home/tarunshah/phantomjs",desired_capabilities=dcap, service_args=['--ignore-ssl-errors=true'])
        # chromedriver = "/Documents/chromedriver"
        # os.environ["webdriver.chrome.driver"] = chromedriver
        # driver = webdriver.Chrome(executable_path=r"/home/tarunshah/Documents/chromedriver")
        driver = webdriver.Chrome()
        loginDetails = login_credentials(filter)
        url = loginDetails[0]['ChannelUrl']

        driver.get(url)
        time.sleep(8)
        # Maximiazing Browser to window size
        # driver.maximize_window()
        # time.sleep(5)

        driver.switch_to.frame(driver.find_element_by_id("overlayRegFrame"))

        email = driver.find_element_by_id("regSignIn.email")
        password = driver.find_element_by_id("regSignIn.password")

        # loginDetails = login_credentials(filter)
        loginId = loginDetails[0]['UserId']
        loginPassword = loginDetails[0]['Password']

        email.send_keys(loginId)
        password.send_keys(loginPassword)


        element = driver.find_element_by_xpath("//*[@id='regSignIn']/div[3]")
        driver.execute_script("arguments[0].click();", element)
        time.sleep(5)

        #app.logger.info("Log IN Tripadvisor")
        driver.get(url)
        time.sleep(5)
        responseDiv = driver.find_elements_by_class_name("response-status")
        # responseDiv = driver.find_element_by_class_name("response-status")
        #responseStatus = responseDiv.find_element_by_tag_name("span").text
        #if responseStatus == "Response Published":
        if responseDiv:
            status = "You have Already Responded"
            DATABASE.hotelData.update({"_id": ObjectId(str(objectId))}, {'$set': {"Replied": "R1"}})
            driver.close()
        else:
            driver.find_element_by_xpath("//select[@id='bizrole']").click()
            # try:
            #     v = driver.find_element_by_xpath('//div[@class="t4b-select-container input-bizrole"]')
            #     v.click()
            # except:
            #     driver.find_element_by_xpath("//select[@id='bizrole']").click()
            driver.find_element_by_xpath("//select[@id='bizrole']/option[@value='Manager']").click()
            textArea = driver.find_element_by_class_name("response-text")
            textArea.send_keys(message)
            driver.find_element_by_class_name("submit").click()
            logging.info("Channel - TripAdvisor Reviewer Replied ObjectId " + str(objectId))
            status = "Responded Successfully"
            DATABASE.hotelData.update({"_id": ObjectId(str(objectId))},{'$set': {"Replied": "R1"}})
            driver.close()
    except Exception as e:
        print(e)
        status = "Something went wrong! Please try again later."
        driver.close()
        name = filter['PropertyName']
        place = filter['PropertyLocation']
        recipients = ["niki.upadhyay@repusight.com", "tarun.shah@repusight.com"]
        esubject = "Error while responding to review on " + datetime.datetime.now().strftime(
            "%d %b, %Y %I:%M:%S %p") + " for Tripadvisor"
        ebody = "For " + name + ", " + place + "\nSome error has occured: \n" + str(e)
        ebody = ebody + "\n\nDetails are, \n" + str(filter)
        ebody = ebody + "\n\n\nRepusight Support."
        send_mail(recipients, esubject, ebody)
    return status


def replyGoibibo(url,rname,message,objectId,filter):
    try:
        driver = webdriver.PhantomJS(desired_capabilities=dcap,service_args=['--ignore-ssl-errors=true'])
        #driver = webdriver.PhantomJS(executable_path=r"/home/tarunshah/phantomjs", desired_capabilities=dcap,service_args=['--ignore-ssl-errors=true'])
        # chromedriver = "/Documents/chromedriver"
        # os.environ["webdriver.chrome.driver"] = chromedriver
        # driver = webdriver.Chrome(executable_path=r"/home/tarunshah/Documents/chromedriver")
        driver.get(url)
        time.sleep(8)
        # Maximiazing Browser to window size
        driver.maximize_window()
        username = driver.find_element_by_id("id_username")
        password = driver.find_element_by_id("id_password")

        loginDetails = login_credentials(filter)
        loginId = loginDetails[0]['UserId']
        loginPassword = loginDetails[0]['Password']

        username.send_keys(loginId)
        password.send_keys(loginPassword)

        driver.find_element_by_xpath("//*[@id='login-form']/div[3]/button").click()
        time.sleep(10)
        driver.find_element_by_xpath("//*[@id='mainTabs']/li[9]/a").click()
        time.sleep(5)
        allCount = int(driver.find_element_by_id("allCount").text)
        loopCount = math.ceil(allCount/10)
        for cnt in range(0,loopCount):
            table = driver.find_element_by_id("review_template")
            trs = table.find_elements_by_class_name("bk_table_cnt")
            for tr in trs:
                bookingID = tr.find_element_by_xpath("td[1]").text
                td3 = tr.find_element_by_xpath("td[3]").text
                td6 = tr.find_element_by_xpath("td[6]").text
                if rname == td3:
                    td8 = tr.find_element_by_xpath("td[8]")
                    statusTxt = td8.find_element_by_xpath("input").get_attribute("value")
                    if bookingID == "Non-Booking Review":
                        td8Id = td8.get_attribute("id")
                        bookingID = td8Id[13:]
                    if statusTxt == "Reply Now":
                        td8.find_element_by_xpath("input").click()
                        time.sleep(5)
                        driver.save_screenshot("scr1.png")
                        reviewArea = driver.find_element_by_xpath("//tr[@class='replyarea "+bookingID+"']")
                        textArea = reviewArea.find_element_by_id("textArea")
                        textArea.send_keys(message)
                        reviewArea.find_element_by_tag_name("button").click()
                        time.sleep(3)
                        confirmModel = driver.find_element_by_class_name("confirm-modification-model")
                        confirmModel.find_element_by_class_name("confirm-send-reply").click()
                        time.sleep(3)
                        logging.info("Channel - Goibibo Reviewer Name - " + rname + " Replied")
                        status = "Responded Successfully"
                        DATABASE.hotelData.update({"_id": ObjectId(str(objectId))},{'$set': {"Replied": "R1"}})
                        driver.close()
                        return status
                    elif statusTxt == "Reply Not Required":
                        status = "Reply Not Required for this"
                        driver.close()
                        return status
                    elif statusTxt == "Replied":
                        status = "You have Already Responded"
                        DATABASE.hotelData.update({"_id": ObjectId(str(objectId))},{'$set': {"Replied": "R1"}})
                        driver.close()
                        return status
                    elif statusTxt == "Pending moderation":
                        status = "You have Pending moderation"
                        DATABASE.hotelData.update({"_id": ObjectId(str(objectId))},{'$set': {"Replied": "R1"}})
                        driver.close()
            element = driver.find_element_by_link_text(">")
            driver.execute_script("arguments[0].click();", element)
            time.sleep(5)
    except Exception as e:
        logging.error(e)
        status = "Something went wrong! Please try again later."
        driver.close()
        name = filter['PropertyName']
        place = filter['PropertyLocation']
        recipients = ["niki.upadhyay@repusight.com", "tarun.shah@repusight.com"]
        esubject = "Error while responding to review on " + datetime.datetime.now().strftime(
            "%d %b, %Y %I:%M:%S %p") + " for Goibibo"
        ebody = "For " + name + ", " + place + "\nSome error has occured: \n" + str(e)
        ebody = ebody + "\n\nDetails are, \n" + str(filter)
        ebody = ebody + "\n\n\nRepusight Support."
        send_mail(recipients, esubject, ebody)
    return status


def replyBooking(url,message,bookingID,objectId,filter):
    try:
        driver = webdriver.PhantomJS(desired_capabilities=dcap,service_args=['--ignore-ssl-errors=true'])
        #driver = webdriver.PhantomJS(executable_path=r"/home/tarunshah/phantomjs", desired_capabilities=dcap,service_args=['--ignore-ssl-errors=true'])
        # chromedriver = "/Documents/chromedriver"
        # os.environ["webdriver.chrome.driver"] = chromedriver
        # driver = webdriver.Chrome(executable_path=r"/home/tarunshah/Documents/chromedriver")
        driver.get(url)
        time.sleep(8)
        # Maximiazing Browser to window size
        driver.maximize_window()
        username = driver.find_element_by_id("loginname")
        password = driver.find_element_by_id("password")

        loginDetails = login_credentials(filter)
        loginId = loginDetails[0]['UserId']
        loginPassword = loginDetails[0]['Password']

        username.send_keys(loginId)
        password.send_keys(loginPassword)

        driver.find_element_by_xpath("//*[@id='wrap']/div[1]/div/section/div/section[1]/div/div/div/div/form/button").click()
        time.sleep(5)
        mainDiv = driver.find_element_by_xpath("//*[@name='"+str(bookingID)+"']/../..")
        if mainDiv.find_elements_by_link_text("Reply"):
            mainDiv.find_element_by_link_text("Reply").click()
            time.sleep(2)
            textarea = mainDiv.find_element_by_tag_name("textarea")
            textarea.send_keys(message)
            mainDiv.find_element_by_class_name("send-reply").click()
            logging.info("Channel - Booking BookingId - " + str(bookingID) + " Replied")
            status = "Responded Successfully"
            DATABASE.hotelData.update({"_id": ObjectId(str(objectId))},{'$set': {"Replied": "R1"}})
            driver.close()
            return status
        elif mainDiv.find_elements_by_link_text("View your response"):
            status = "Your response is awaiting approval."
        elif mainDiv.find_elements_by_link_text("View your approved response"):
            status = "You have Already Responded"
        driver.close()
    except Exception as e:
        logging.error(e)
        status = "Something went wrong! Please try again later."
        driver.close()
        name = filter['PropertyName']
        place = filter['PropertyLocation']
        recipients = ["niki.upadhyay@repusight.com", "tarun.shah@repusight.com"]
        esubject = "Error while responding to review on " + datetime.datetime.now().strftime(
            "%d %b, %Y %I:%M:%S %p") + " for Booking"
        ebody = "For " + name + ", " + place + "\nSome error has occured: \n" + str(e)
        ebody = ebody + "\n\nDetails are, \n" + str(filter)
        ebody = ebody + "\n\n\nRepusight Support."
        send_mail(recipients, esubject, ebody)
    return status


def replyZomato(url, reviewID, message,objectId,filter):
    try:
        # chromedriver = "/Documents/chromedriver"
        # os.environ["webdriver.chrome.driver"] = chromedriver
        # driver = webdriver.Chrome(executable_path=r"/home/tarunshah/Documents/chromedriver")
        driver = webdriver.Chrome()
        driver.get(url)
        time.sleep(8)
        # # Maximiazing Browser to window size
        driver.maximize_window()
        time.sleep(5)
        model = driver.find_element_by_id("modal-container")
        model.find_element_by_class_name("login-icons").click()
        time.sleep(5)

        email = driver.find_element_by_id("ld-email")
        password = driver.find_element_by_id("ld-password")

        loginDetails = login_credentials(filter)
        loginId = loginDetails[0]['UserId']
        loginPassword = loginDetails[0]['Password']

        email.send_keys(loginId)
        password.send_keys(loginPassword)

        driver.find_element_by_id("ld-submit-global").click()
        time.sleep(5)
        driver.find_element_by_id("li_all").click()
        time.sleep(3)

        Tag = True
        while Tag:
            mainDiv = driver.find_elements_by_xpath("//div[@data-review_id=" + str(reviewID) + "]")
            if mainDiv:
                replyDiv = driver.find_element_by_id("rrtr-"+ str(reviewID))
                if replyDiv.find_elements_by_class_name("review-reply-text"):
                    status = "You have Already Responded"
                    DATABASE.restaurantData.update({"_id": ObjectId(str(objectId))},{'$set': {"Replied": "R1"}})
                    driver.close()
                    Tag = False
                else:
                    textArea = mainDiv[0].find_element_by_class_name("review-replies-new-textbox-dash")
                    textArea.send_keys(message)
                    mainDiv[0].find_element_by_class_name("review-replies-new-submit-dash").click()
                    status = "Responded Successfully"
                    DATABASE.restaurantData.update({"_id": ObjectId(str(objectId))},{'$set': {"Replied": "R1"}})
                    logging.info("Channel - Zomato Reviewer Id - " + str(reviewID) + " Replied")
                    driver.close()
                    Tag = False
            else:
                if driver.find_elements_by_class_name("load-more"):
                    driver.find_element_by_class_name("load-more").click()
                    time.sleep(5)
                else:
                    status = "No comment found !!"
                    driver.close()
    except Exception as e:
        logging.error(e)
        status = "Something went wrong! Please try again later."
        driver.close()
        name = filter['PropertyName']
        place = filter['PropertyLocation']
        recipients = ["niki.upadhyay@repusight.com", "tarun.shah@repusight.com"]
        esubject = "Error while responding to review on " + datetime.datetime.now().strftime(
            "%d %b, %Y %I:%M:%S %p") + " for Zomato"
        ebody = "For " + name + ", " + place + "\nSome error has occured: \n" + str(e)
        ebody = ebody + "\n\nDetails are, \n" + str(filter)
        ebody = ebody + "\n\n\nRepusight Support."
        send_mail(recipients, esubject, ebody)
    return status


def replyHolidayIQ(url,name,message,objectId,filter):
    try:
        driver = webdriver.PhantomJS(desired_capabilities=dcap,service_args=['--ignore-ssl-errors=true'])
        #driver = webdriver.PhantomJS(executable_path=r"/home/tarunshah/phantomjs", desired_capabilities=dcap,service_args=['--ignore-ssl-errors=true'])
        # chromedriver = "/Documents/chromedriver"
        # os.environ["webdriver.chrome.driver"] = chromedriver
        # driver = webdriver.Chrome(executable_path=r"/home/tarunshah/Documents/chromedriver")
        #driver = webdriver.Chrome()
        driver.get(url)
        time.sleep(8)
        # Maximiazing Browser to window size
        driver.maximize_window()

        username = driver.find_element_by_id("exampleInputEmail1")
        password = driver.find_element_by_id("exampleInputPassword1")

        loginDetails = login_credentials(filter)
        loginId = loginDetails[0]['UserId']
        loginPassword = loginDetails[0]['Password']

        username.send_keys(loginId)
        password.send_keys(loginPassword)

        driver.find_element_by_class_name("btn").click()

        time.sleep(5)

        while driver.find_element_by_xpath("//a[@rel='next']"):

            table = driver.find_element_by_id("reviewListTable")
            rows = table.find_elements_by_class_name("review-row")

            for row in rows:
                tds = row.find_elements_by_tag_name("td")
                rname = tds[3].text
                rname = rname.replace(" ", "")
                name = name.replace(" ","")
                if name == rname:
                    print(tds[6].text)
                    if tds[6].text == "Inprocess":
                        status = "Your Reply is in process"
                        DATABASE.hotelData.update({"_id": ObjectId(str(objectId))}, {'$set': {"Replied": "R1"}})
                        driver.close()
                    elif "Approved" in tds[6].text:
                        status = "You have Already Responded"
                        DATABASE.hotelData.update({"_id": ObjectId(str(objectId))}, {'$set': {"Replied": "R1"}})
                        driver.close()
                    else:
                        tds[6].find_element_by_tag_name("button").click()
                        id = tds[1].find_element_by_id("rate_sheet_id").get_attribute("value")
                        ele = driver.find_element_by_class_name("response-tab-"+str(id))
                        comment = ele.find_element_by_id("comment")
                        comment.send_keys(message)
                        ele.find_element_by_class_name("btn-success").click()
                        time.sleep(3)
                        logging.info("Channel - HolidayIQ Reviewer Name - " + name + " Replied")
                        status = "Responded Successfully"
                        DATABASE.hotelData.update({"_id": ObjectId(str(objectId))},{'$set': {"Replied": "R1"}})
                        driver.close()
                    return status
                else:
                    status = "Something went wrong! Please try again later."
            driver.find_element_by_xpath("//a[@rel='next']").click()
    except Exception as e:
        logging.error(e)
        status = "Something went wrong! Please try again later."
        driver.close()
        name = filter['PropertyName']
        place = filter['PropertyLocation']
        recipients = ["niki.upadhyay@repusight.com", "tarun.shah@repusight.com"]
        esubject = "Error while responding to review on " + datetime.datetime.now().strftime(
            "%d %b, %Y %I:%M:%S %p") + " for HolidayIQ"
        ebody = "For " + name + ", " + place + "\nSome error has occured: \n" + str(e)
        ebody = ebody + "\n\nDetails are, \n" + str(filter)
        ebody = ebody + "\n\n\nRepusight Support."
        send_mail(recipients, esubject, ebody)
    return status


def replyGoogle(url,message,rname,objectId,filter):
    try:
        driver = webdriver.PhantomJS(desired_capabilities=dcap,service_args=['--ignore-ssl-errors=true'])
        #driver = webdriver.PhantomJS(executable_path=r"/home/tarunshah/phantomjs",desired_capabilities=dcap, service_args=['--ignore-ssl-errors=true'])
        # chromedriver = "/Documents/chromedriver"
        # os.environ["webdriver.chrome.driver"] = chromedriver
        # driver = webdriver.Chrome(executable_path=r"/home/tarunshah/Documents/chromedriver")
        driver.get(url + "0")
        time.sleep(5)
        # Maximiazing Browser to window size
        # driver.maximize_window()
        # time.sleep(5)

        loginDetails = login_credentials(filter)
        loginId = loginDetails[0]['UserId']
        loginPassword = loginDetails[0]['Password']
        backupNo = loginDetails[0]['backupNo']
        email = driver.find_element_by_id("identifierId")
        email.send_keys(loginId)
        driver.find_element_by_id("identifierNext").click()
        time.sleep(5)
        password = driver.find_element_by_xpath("//*[@id='password']/div[1]/div/div[1]/input")
        password.send_keys(loginPassword)
        driver.find_element_by_id("passwordNext").click()
        time.sleep(3)
        driver.save_screenshot("scr1.png")
#        element = driver.find_element_by_xpath("//*[@id='view_container']/form/div[2]/div/div/div/ul/li[3]/div/div[2]")
#        element.click()
        time.sleep(1)
        try:
            phoneNo = driver.find_element_by_id("phoneNumberId")
            time.sleep(1)
            phoneNo.send_keys(backupNo)
            time.sleep(1)
            driver.find_element_by_id("next").click()
            time.sleep(3)
        except NoSuchElementException:
            pass
        noOfReviews = driver.find_element_by_xpath("//div[@id='main_viewpane']/div/c-wiz/div/div/div[3]/p").text
        noOfReviews = noOfReviews.strip()
        count = math.ceil(noOfReviews/10)
        for i in range(1,count):
            allElements = driver.find_elements_by_class_name("PD")
            for element in allElements:
                name = element.find_element_by_class_name("tX").text
                if name == rname:
                    responseStatus = element.find_elements_by_link_text("View and edit response")
                    if responseStatus:
                        status = "You have Already Responded"
                        logging.info("Channel - GoogleReview Reviewer Name - " + rname + "  Already Responded")
                        DATABASE.hotelData.update({"_id": ObjectId(str(objectId))},{'$set': {"Replied": "R1"}})
                        driver.close()
                        return status
                    else:
                        element.find_element_by_link_text("View and reply").click()
                        time.sleep(1)
                        textarea = driver.find_element_by_tag_name("textarea")
                        textarea.send_keys(message)
                        driver.find_element_by_xpath("//*[@id='main_viewpane']/div[3]/div/div/div/div[3]/div/div[1]/div[4]/div[2]/div[1]").click()
                        time.sleep(2)
                        logging.info("Channel - GoogleReview Reviewer Name - " + rname + " Replied")
                        status = "Responded Successfully"
                        DATABASE.hotelData.update({"_id": ObjectId(str(objectId))}, {'$set': {"Replied": "R1"}})
                        driver.close()
                        return status
            driver.get(url+ str(i))
            time.sleep(5)
    except (Exception) as e:
        logging.error(e)
        status = "Something went wrong! Please try again later."
        driver.close()
        name = filter['PropertyName']
        place = filter['PropertyLocation']
        recipients = ["niki.upadhyay@repusight.com", "tarun.shah@repusight.com"]
        esubject = "Error while responding to review on " + datetime.datetime.now().strftime(
            "%d %b, %Y %I:%M:%S %p") + " for Google"
        ebody = "For " + name + ", " + place + "\nSome error has occured: \n" + str(e)
        ebody = ebody + "\n\nDetails are, \n" + str(filter)
        ebody = ebody + "\n\n\nRepusight Support."
        send_mail(recipients, esubject, ebody)
    return status


def maindef():
    data = list(DATABASE.replies.find({"RepliedStatus":None}))
    print(data)
    for replies in data:
        source = replies["Source"]
        if source == "TripAdvisor":
            url = "https://www.tripadvisor.in/OwnerResponse-g297628-d3365457-Reviews-Davanam_Sarovar_Portico_Suites-Bengaluru_Karnataka.html?review=" + str(
                replies["reviewID"])
            status = replyTripadvisor(url=url, message=replies["ReplyText"], objectId=replies["CommentId"], filter=replies)
            if status != "Something went wrong! Please try again later.":
                DATABASE.replies.update({"CommentId": str(replies["CommentId"])}, {'$set': {"RepliedStatus": status}})
        elif source == "Goibibo":
            url = "http://in.goibibo.com/accounts/login/?next=/extranet/"
            status = replyGoibibo(url=url, rname=replies["ReviewerName"], message=replies["ReplyText"], objectId=replies["CommentId"], filter=replies)
            if status != "Something went wrong! Please try again later.":
                DATABASE.replies.update({"CommentId": str(replies["CommentId"])},
                                                    {'$set': {"RepliedStatus": status}})
        elif source == "Booking":
            url = "https://admin.booking.com/hotel/hoteladmin/extranet_ng/manage/reviews.html"
            bookingID = replies["reviewID"]
            status = replyBooking(url=url, message=replies["ReplyText"], bookingID=bookingID, objectId=replies["CommentId"], filter=replies)
            if status != "Something went wrong! Please try again later.":
                DATABASE.replies.update({"CommentId": str(replies["CommentId"])},
                                                    {'$set': {"RepliedStatus": status}})
        elif source == "Zomato":
            details = list(DATABASE.zmEntityId.find({'Name': replies["PropertyName"], 'Place': replies["PropertyLocation"]}))
            entityId = details[0]['EntityId']
            now_date = datetime.date.today()
            url = "https://www.zomato.com/clients/reviews_new.php?entity_type=restaurant&entity_id=" + str(
                entityId) + "&start_date=2012-01-01&end_date=" + str(now_date)
            status = replyZomato(url=url, reviewID=replies["reviewID"], message=replies["ReplyText"], objectId=replies["CommentId"], filter=replies)
            if status != "Something went wrong! Please try again later.":
                DATABASE.replies.update({"CommentId": str(replies["CommentId"])},
                                                    {'$set': {"RepliedStatus": status}})
        elif source == "HolidayIQ":
            url = "http://www.holidayiq.com/business/dashboard?resort_id=421493"
            status = replyHolidayIQ(url=url, name=replies["ReviewerName"], message=replies["ReplyText"], objectId=replies["CommentId"], filter=replies)
            if status != "Something went wrong! Please try again later.":
                DATABASE.replies.update({"CommentId": str(replies["CommentId"])},
                                                    {'$set': {"RepliedStatus": status}})
        elif source == "GoogleReview":
            url = "https://business.google.com/b/117378744535000800155/reviews/l/07551163536708814495/"
            status = replyGoogle(url=url, message=replies["ReplyText"], rname=replies["ReviewerName"], objectId=replies["CommentId"], filter=replies)
            if status != "Something went wrong! Please try again later.":
                DATABASE.replies.update({"CommentId": str(replies["CommentId"])},
                                                    {'$set': {"RepliedStatus": status}})
        else:
            status = "Something went wrong! Please try again later."


# if __name__ == "__main__":
#     main()