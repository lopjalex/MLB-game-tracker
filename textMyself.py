#! /usr/bin/env python3
# textMyself.py - Defines the textmyself() function that texts a message
# passed to it as a string.

# Present values:
accountSID = ''
authToken = ''
myNumber = ''
twilioNumber = ''

from twilio.rest import Client

def textmyself(message):
    client = Client(accountSID, authToken)
    client.messages.create(body = message, from_ = twilioNumber, to = myNumber)