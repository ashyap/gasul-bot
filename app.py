#Python libraries that we need to import for our bot
import random
import requests
import os
import json
from flask import Flask, request
from pymessenger.bot import Bot
from pymessenger import Element, Button
import os

app = Flask(__name__)

#We will receive messages that Facebook sends our bot at this endpointc
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    branch_list = ["Buhangin-1", "Buhangin-2", "Cabantian", "Dona Pilar",
                   "Monteverde", "R. Castillo", "Sasa", "Sobrecary",
                   "Damosa"]

    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       print(output)
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']
                if message['message'].get('text'):
                    return get_message(message['message'].get('text'),
                                       recipient_id,
                                       branch_list)
            elif message.get('postback') :
                recipient_id = message['sender']['id']
                print(recipient_id)
                if message['postback'].get('payload') == 'branches':
                    send_branches(recipient_id, branch_list)
                elif message['postback'].get('payload') == 'prices':
                    send_products(recipient_id)
                elif message['postback'].get('payload') == 'schedule':
                    return send_message(recipient_id, "Operating hours are "
                                        + "from Mon. to Sat. 8am to 5:30pm. "
                                        + "You may contact us at 226-2992 "
                                        + "or 0999-889-6448")
                elif (message['postback'].get('payload') == 'help' or
                     message['postback'].get('payload').lower() == 'get started'):
                    return send_menu(recipient_id)
    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


#chooses a random message to send to the user
def get_message(text, recipient_id, branch_list):
    if text.lower() == 'help':
        branches_button = Button(title='Branches', type='postback', payload='branches')
        hours_button = Button(title='Contact Info & Store Hours', type='postback', payload='schedule')
        prices_button = Button(title='Price Check', type='postback', payload='prices')
        buttons = [branches_button, hours_button, prices_button]
        text = 'Hi! how may I help you?'
        result = bot.send_button_message(recipient_id, text, buttons)
        return "success"
    elif text.lower() == '11kg':
        send_message(recipient_id, '11kg content only is P848, Prices are '
                     + 'subject to change without notice')
        bot.send_image_url(recipient_id, "https://i.imgur.com/zw5XWAc.jpg")
        return "success"
    elif text.lower() == '2.7kg':
        send_message(recipient_id, '2.7kg content only is P275, Prices are '
                     + 'subject to change without notice')
        bot.send_image_url(recipient_id, "https://i.imgur.com/CQPAgOA.jpg")
        return "success"
    elif text.lower() == '7kg':
        send_message(recipient_id, '7kg content only is P549, Prices are '
                     + 'subject to change without notice')
        bot.send_image_url(recipient_id, "https://i.imgur.com/5tdOCwY.jpg")
        return "success"
    elif text.lower() in [x.lower() for x in branch_list]:
        lat = ''
        long = ''
        number = ''
        print(branch_locations)
        for branch_loc in branch_locations['branches']:
            if branch_loc['branch'] == text.lower():
                lat = branch_loc['lat']
                long = branch_loc['long']
                number = branch_loc['number']
                break
        url = "https://www.google.com/maps/dir/?api=1&destination={}%2C{}&travelmode=walking".format(lat,long)
        payload = {
          "template_type":"generic",
          "elements":[
             {
              "title": text.lower(),
              "image_url": "https://i.imgur.com/5tdOCwY.jpg",
              "subtitle": number,
              "default_action": {
                "type": "web_url",
                "url": url,
                "messenger_extensions": "FALSE",
                "webview_height_ratio": "COMPACT"
              },
            }
          ]
        }
        send_message(recipient_id, 'Click the link below to see the '
                     + 'branch location.')
        bot.send_message(recipient_id, {
            'attachment':{
                'type': 'template',
                'payload': payload
            }
        })
        return "success"

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

def send_branches(recipient_id, branch_list):
    branch_list = sorted(branch_list)
    quick_replies = []

    for branch in branch_list:
        quick_replies.append({
            "content_type": "text",
            "title": branch,
            "payload": branch.lower()
        })
    bot.send_message(recipient_id, {'text': 'Pick a branch near you',
                                    'quick_replies': quick_replies})
    return "success"

def send_products(recipient_id):
    product_list = ["11kg", "7kg", "2.7kg"]
    product_list = sorted(product_list)
    quick_replies = []

    for product in product_list:
        quick_replies.append({
            "content_type": "text",
            "title": product,
            "payload": product.lower()
        })
    bot.send_message(recipient_id, {'text': 'Pick a product',
                                    'quick_replies': quick_replies})
    return "success"

def send_menu(recipient_id):
    branches_button = Button(title='Branches', type='postback', payload='branches')
    hours_button = Button(title='Store Hours & Contact Info', type='postback', payload='schedule')
    prices_button = Button(title='Price Check', type='postback', payload='prices')
    buttons = [branches_button, hours_button, prices_button]
    text = 'Hi! how may I help you?'
    result = bot.send_button_message(recipient_id, text, buttons)
    return 'success'

def set_persistent_menu(access_token):
    url = "https://graph.facebook.com/v2.6/me/messenger_profile?access_token={}".format(access_token)

    payload = {
      "get_started": {
        "payload": "Get started"
      },
      "persistent_menu":[
        {
          "locale":"default",
          "composer_input_disabled": 'false',
          "call_to_actions":[
            {
              "title":"Ask Help",
              "type":"postback",
              "payload":"help"
            }
          ]
        }
      ]
    }

    response = requests.post(
        url,
        json=payload
    )
    return response.json()

ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']

bot = Bot (ACCESS_TOKEN)
branch_locations = []
with open("branches.json") as f:
    branch_locations = json.load(f)

set_persistent_menu(ACCESS_TOKEN)

if __name__ == "__main__":
    app.run()
