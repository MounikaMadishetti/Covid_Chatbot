from flask import Flask, request, make_response
import requests
from requests.exceptions import HTTPError
import re

import json
import os
from flask_cors import cross_origin
from SendEmail.sendEmail import EmailSender
from config_reader import ConfigReader

app = Flask(__name__)


# geting and sending response to dialogflow
@app.route('/webhook', methods=['POST'])
@cross_origin()
def webhook():
    config_reader = ConfigReader()
    configuration = config_reader.read_config()



    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    intent_check = req.get("queryResult").get("intent").get("displayName")

    if intent_check == "CountryCases_menu":
        res = getCountryName(req)
    elif intent_check == "StateCases_menu":
        res = getStateName(req)
    elif intent_check == "MyAreaCases_menu":
        res = getUserDetails(req)
    elif intent_check == "GlobalCases_menu":
        res = globalCases(req)
    elif intent_check == "indiaCases_menu":
        res = indiaCases(req)
    elif intent_check == "News":
        res = news(req)
    elif intent_check == "Helpline_Menu":
        res = helpLine(req)

    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r



def helpLine(req):
    return {
        "fulfillmentText": "hello1"
    }
    result = req.get("queryResult")
    user_says = result.get("queryText")
    state = result.get("parameters").get("state_name")
    state = state.lower()
    state = state.title()


    try:
        return {
            "fulfillmentText": "hello"
        }
        url = "https://api.rootnet.in/covid19-in/contacts.json"
        res = requests.get(url)
        jsonRes = res.json()
        stateWiseCases = jsonRes["regional"]
        for i in range(len(stateWiseCases)):
            if stateWiseCases[i]["loc"] == state:

                helpLineNum = str(stateWiseCases[i]["deaths"])
                fulfillmentText = "Help Line number of " + state + "is" + helpLineNum
                bot_says = fulfillmentText

                return {
                    "fulfillmentText": fulfillmentText
                }
        else:
            fulfillmentText = "Sorry we could not find any state named " + state + ". It might be a misspelling or we don't have record of the state."
            bot_says = fulfillmentText

            return {
                "fulfillmentText": fulfillmentText
            }

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


def getCountryName(req):

    result = req.get("queryResult")
    user_says = result.get("queryText")
    country = result.get("parameters").get("country_name")
    country = country.lower()
    country = country.title()
    try:
        url = "https://corona.lmao.ninja/v2/countries/" + country
        res = requests.get(url)
        jsonRes = res.json()
        countryWiseCases = jsonRes
        if countryWiseCases["country"]:
            confirmed = str(countryWiseCases["cases"])
            recovered = str(countryWiseCases["recovered"])
            deaths = str(countryWiseCases["deaths"])
            fulfillmentText = country + " stats of COVID-19 are: \nConfirmed Cases: " + confirmed + "\nRecovered Cases: " + recovered + "\nDeaths: " + deaths
            bot_says = fulfillmentText

            return {
                "fulfillmentText": fulfillmentText
            }
        else:
            fulfillmentText = "Sorry we could not find any country named " + country + ". It might be a misspelling or we don't have record of the country."
            bot_says = fulfillmentText

            return {
                "fulfillmentText": fulfillmentText
            }

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return {
            "fulfillmentText": "lskdfj"
        }
    except Exception as err:
        return {
            "fulfillmentText": "oihf"
        }
        print(f"Other error occurred: {err}")


def getStateName(req):
    sessionID = req.get("session")
    session = re.compile("sessions/(.*)")
    sessionID = session.findall(sessionID)[0]
    result = req.get("queryResult")
    user_says = result.get("queryText")
    state = result.get("parameters").get("state_name")
    state = state.lower()
    state = state.title()
    if "&" in state:
        state = state.replace("&", "and")
    if state == "Tamilnadu":
        state = "Tamil Nadu"
    try:
        url = "https://api.covid19india.org/data.json"
        res = requests.get(url)
        jsonRes = res.json()
        stateWiseCases = jsonRes["statewise"]
        for i in range(len(stateWiseCases)):
            if stateWiseCases[i]["state"] == state:
                confirmed = str(stateWiseCases[i]["confirmed"])
                active = str(stateWiseCases[i]["active"])
                recovered = str(stateWiseCases[i]["recovered"])
                deaths = str(stateWiseCases[i]["deaths"])
                fulfillmentText = state + " stats of COVID-19 are: \nConfirmed Cases: " + confirmed + "\nActive Cases: " + active + "\nRecovered Cases: " + recovered + "\nDeaths: " + deaths
                bot_says = fulfillmentText

                return {
                    "fulfillmentText": fulfillmentText
                }
        else:
            fulfillmentText = "Sorry we could not find any state named " + state + ". It might be a misspelling or we don't have record of the state."
            bot_says = fulfillmentText

            return {
                "fulfillmentText": fulfillmentText
            }

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


def getUserDetails(req):

    result = req.get("queryResult")
    user_says = result.get("queryText")
    name = result.get("parameters").get("user_name")
    email = result.get("parameters").get("user_mail")
    mobile = result.get("parameters").get("user_phone")
    pincode = result.get("parameters").get("user_pin")




    try:
        url = "https://api.postalpincode.in/pincode/" + pincode


        res = requests.get(url)
        jsonRes = res.json()
        postOffice = jsonRes[0]["PostOffice"]
        state = str(postOffice[0]["State"])
        if "&" in state:
            state = state.replace("&", "and")
        district = str(postOffice[0]["District"])
        if "&" in district:
            district = district.replace("&", "and")
        if district == "Ahmedabad":
            district = "Ahmadabad"
        elif district == "Bangalore":
            district = "Bengaluru"
        elif district == "Central Delhi":
            district = "New Delhi"
        print(state, end=',')
        print(district)
        try:
            url1 = "https://api.covid19india.org/v2/state_district_wise.json"
            res1 = requests.get(url1)
            jsonRes1 = res1.json()
            stateDistrictData = jsonRes1


            for i in range(len(stateDistrictData)):

                stateDistrictData1 = stateDistrictData[i]
                if stateDistrictData1["state"] == state:
                    
                    districtData = stateDistrictData1["districtData"]
                    for j in range(len(districtData)):
                        email_sender = EmailSender()
                        if districtData[j]["district"] == district:
                            confirmed = str(districtData[j]["confirmed"])
                            print(f"\n Confirmed Cases are: {confirmed}")
                            email_file = open(
                                "email-templates/email-template-district.html", "r")
                            email_message = email_file.read()
                            email_sender.sendEmailDistrict(
                                name, email, district, confirmed, email_message)
                            fulfillmentText = "A mail has been sent to you with current COVID-19 cases in your area."
                            bot_says = fulfillmentText

                            return {
                                "fulfillmentText": fulfillmentText
                            }
                    else:
                        fulfillmentText = "Sorry we did not found any data of COVID-19 in " + district + ". It might be a misspelling or we don't have record of the district."
                        bot_says = fulfillmentText

                        return {
                            "fulfillmentText": fulfillmentText
                        }

        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


def globalCases(req):

    result = req.get("queryResult")
    user_says = result.get("queryText")
    try:
        url = "https://api.covid19api.com/summary"
        res = requests.get(url)
        jsonRes = res.json()
        totalGlobalCases = jsonRes["Global"]
        confirmed = str(totalGlobalCases["TotalConfirmed"])
        recovered = str(totalGlobalCases["TotalRecovered"])
        deaths = str(totalGlobalCases["TotalDeaths"])
        fulfillmentText = "Confirmed Cases: " + confirmed + "\nRecovered Cases: " + recovered + "\nDeaths: " + deaths
        bot_says = fulfillmentText

        return {
            "fulfillmentText": fulfillmentText
        }

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")



def indiaCases(req):

    result = req.get("queryResult")
    user_says = result.get("queryText")
    try:
        url = "https://api.covid19india.org/data.json"
        res = requests.get(url)
        jsonRes = res.json()
        totalIndiaCases = jsonRes["statewise"][0]
        confirmed = str(totalIndiaCases["confirmed"])
        active = str(totalIndiaCases["active"])
        recovered = str(totalIndiaCases["recovered"])
        deaths = str(totalIndiaCases["deaths"])
        fulfillmentText = "Confirmed Cases: " + confirmed + "\nActive Cases: " + active + "\nRecovered Cases: " + recovered + "\nDeaths: " + deaths
        bot_says = fulfillmentText

        return {
            "fulfillmentText": fulfillmentText
        }

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


def news(req):
    sessionID = req.get("session")
    session = re.compile("sessions/(.*)")
    sessionID = session.findall(sessionID)[0]
    result = req.get("queryResult")
    user_says = result.get("queryText")
    try:
        config_reader = ConfigReader()
        configuration = config_reader.read_config()
        url = "http://newsapi.org/v2/top-headlines?country=in&category=health&apiKey=" + \
            configuration['NEWS_API']
        res = requests.get(url)
        jsonRes = res.json()
        articles = jsonRes["articles"]
        news = list()
        for i in range(len(articles)):
            title = articles[i]["title"]
            author = articles[i]["author"]
            news_final = str(i + 1) + ". " + \
                str(title) + " - " + str(author)
            news.append(news_final)
        fulfillmentText = "\n".join(news)
        bot_says = fulfillmentText

        return {
            "fulfillmentText": fulfillmentText
        }

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host="0.0.0.0")
