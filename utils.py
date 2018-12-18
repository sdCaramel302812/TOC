import requests
import os
import json
from requests_toolbelt import MultipartEncoder
from pymessenger.bot import Bot
from pymessager.message import Messager
import urllib3

GRAPH_URL = "https://graph.facebook.com/v2.6"
ACCESS_TOKEN = "EAAEIZB7isbg0BAMLpqqLFL6bBmlVeD18Bxf1UnMdZBhY0GFT2R4YKHD5OYwxhPXaI2OyoVMAvJt4ugazPtOk5tcmqFQ9LAZBMWdbURcK9kNXhYLwXAO5HgAB6XSfb2cNqZBPByPLWaJCFleCSDCGS1hj3E3tws951bZCwZAn8a5wZDZD"#os.environ.get("ACCESS_TOKEN")


def send_text_message(id, text):
    url = "{0}/me/messages?access_token={1}".format(GRAPH_URL, ACCESS_TOKEN)
    payload = {
        "recipient": {"id": id},
        "message": {"text": text}
    }
    response = requests.post(url, json=payload)

    if response.status_code != 200:
        print("Unable to send message: " + response.text)
    return response

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
        'referer': 'https://www.pixiv.net/'
    }

def send_image_message(recipient_id, img_url):
    bot = Bot(ACCESS_TOKEN)
    print(img_url)
    re = bot.send_image_url(recipient_id, img_url)
    print(re)
    #bot.send_raw(recipient_id, re.raw)
    #bot = Messager(ACCESS_TOKEN)
    #bot.send_image(recipient_id, img_url)
#    url = "{0}/me/messages?access_token={1}".format(GRAPH_URL, ACCESS_TOKEN)
#    payload = {
#        "recipient": {"id": recipient_id},
#        "message": {
#            "attachment":{
#                "type":"image", 
#                "payload": {
#                    "image_url": img_url, 
#                    "is_reusable": True
#                }
#            }
#        }
#    }
#    response = requests.post(url, json=payload, headers=headers)

"""
def send_image_url(id, img_url):
    pass

def send_button_message(id, text, buttons):
    pass
"""
