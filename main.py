import os
import time
import requests
import pandas as pd
from datetime import datetime
from playsound import playsound
from twilio.rest import Client


# class for holding current price of crypto coins
class cryptoCoinPresent:

    def __init__(self, name, currentPrice, lowestPrice, highestPrice, time):
        self.name = name
        self.currentPrice = currentPrice
        self.lowestPrice = lowestPrice
        self.highestPrice = highestPrice
        self.time = time


# class for holing past 15 minutes price state for crypto coins
class cryptoCoinPast:

    def __init__(self, name, currentPrice, lowestPrice, highestPrice, time):
        self.name = name
        self.currentPrice = currentPrice
        self.lowestPrice = lowestPrice
        self.highestPrice = highestPrice
        self.time = time


# global data variables............

# current data price holders
crypto_inr_list_current = []
# past data price holders
crypto_inr_list_past = []
# when the last price data was updated
last_past_update_time = 0
# update the price data after how many minutes
update_time_in_minutes = 30
# set the increase percentage of price
increase_price_percentage = 10
# to set the decrease percentage of price
decrease_price_percentage = 2
# to know when the last sms was sent to your phone
last_sms_sent_time = 0
# to set a timeout for sms being sent to your phone
time_difference_for_sms_sent = 30
# currency val
currency = "inr"


# to update the current price of crypto
def updatingcurrentlist():
    global crypto_inr_list_current
    response = requests.get("https://api.wazirx.com/sapi/v1/tickers/24hr")
    if response.status_code == 200:
        crypto_inr_list_current = []
        data = pd.read_json(response.text)
        print(str(data))
        for index in range(0, len(data)):
            if data['quoteAsset'][index] == currency:
                crypto_inr_list_current.append(cryptoCoinPresent(data['symbol'][index], data['askPrice'][index],
                                                                 data['lowPrice'][index], data['highPrice'][index],
                                                                 data['at'][index]))


# this function should be executed after every minute to update current crypto price and also to make decisions
def updatingdata():
    # print("\nupdating data.....  ")
    # update current
    updatingcurrentlist()

    # check if this is the first time executing the updating data
    global crypto_inr_list_past
    if len(crypto_inr_list_past) == 0:
        global last_past_update_time
        last_past_update_time = datetime.now()
        crypto_inr_list_past = crypto_inr_list_current

    # to check if the crypto is increased by 10%
    increase_sms_message = checkincrease()

    # to check if the crypto has decreased by 10%
    decrease_sms_message = checkdecrease()

    # now determine if we need to send message to my phone
    whole_sms_message = increase_sms_message + "  " + decrease_sms_message
    if len(whole_sms_message) > 10:
        sendsms(whole_sms_message)

    # update the past crypto price after every 15 minutes
    timedifference = (datetime.now() - last_past_update_time).total_seconds() / 60.0
    if timedifference > update_time_in_minutes:
        # print("\n updating past...   ")
        last_past_update_time = datetime.now()
        crypto_inr_list_past = crypto_inr_list_current


def checkincrease():
    # print("\ncheck increase.....   ")
    # hold list for all increased crypto
    increased_crypto_list = []
    increased_percent = []
    past_price = []

    for index in range(0, len(crypto_inr_list_current)):
        present = crypto_inr_list_current[index]
        past = crypto_inr_list_past[index]
        price_difference = present.currentPrice - past.currentPrice
        percent_difference = (price_difference / past.currentPrice) * 100
        if percent_difference >= increase_price_percentage:
            increased_crypto_list.append(crypto_inr_list_current[index])
            increased_percent.append(round(percent_difference, 2))
            past_price.append(past.currentPrice)

    # print all crypto's that have surpassed increase pointer
    message = printcryptolist(increased_crypto_list, increased_percent, past_price)
    return message


def checkdecrease():
    # print("\ncheck decrease.....   ")
    # hold list for all decrease crypto
    decrease_crypto_list = []
    decrease_percent = []
    past_price = []

    for index in range(0, len(crypto_inr_list_current)):
        present = crypto_inr_list_current[index]
        past = crypto_inr_list_past[index]
        price_difference = present.currentPrice - past.currentPrice
        percent_difference = (price_difference / past.currentPrice) * 100
        if percent_difference <= (decrease_price_percentage * -1):
            decrease_crypto_list.append(crypto_inr_list_current[index])
            decrease_percent.append(round(percent_difference, 2))
            past_price.append(past.currentPrice)

    # print all crypto's that have surpassed decrease pointer
    message = printcryptolist(decrease_crypto_list, decrease_percent, past_price)
    return message


# function to print crypto list
def printcryptolist(cryptolist, percentlist, pastpricelist):
    sms_message = ""
    for index in range(0, len(cryptolist)):
        sms_message += "\n\nName: " + str(cryptolist[index].name) + "  Current Price: " + str(
            cryptolist[index].currentPrice) + " Past Price: " + str(
            pastpricelist[index]) + "  Percentage Change: " + str(percentlist[index]) + " Date Time: " + str(datetime.now())
        print("\n\nName: " + str(cryptolist[index].name) + "  Current Price: " + str(
            cryptolist[index].currentPrice) + " Past Price: " + str(
            pastpricelist[index]) + "  Percentage Change: " + str(percentlist[index]))

    return sms_message


# to send text message to my mobile number containing crypto increase and decrease price list
def sendsms(smsMessage):

    audio_file = os.path.dirname(__file__) + '\ornado.mp3'
    playsound(audio_file)
    global last_sms_sent_time

    account_sid = "AC321acc9f98a3b127b87630b0f8cd21f1"
    auth_token = "3eec86291e5e76a99fd7ee3b4345b7a8"
    client = Client(account_sid, auth_token)
    timedifference = 0
    if last_sms_sent_time != 0:
        timedifference = (datetime.now() - last_sms_sent_time).total_seconds() / 60.0
    if timedifference > time_difference_for_sms_sent or last_sms_sent_time == 0:
        message = client.messages.create(
            messaging_service_sid='MGd65adbac45b5e6b704dd05b8357a14ae',
            body=smsMessage,
            to='+917238045397'
        )
        print(message.sid)
        last_sms_sent_time = datetime.now()




while 1:
    updatingdata()
    time.sleep(60)
