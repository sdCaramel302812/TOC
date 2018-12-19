from bottle import route, run, request, abort, static_file
import os
from fsm import TocMachine
from utils import send_text_message, send_image_message
import requests
from bs4 import BeautifulSoup
import json

#nothing change but recommit

VERIFY_TOKEN = os.environ['VERIFY_TOKEN']#"HdksU65463"#os.environ.get("ACCESS_TOKEN")
PORT = os.environ['PORT']
machine = TocMachine(
    states=[
        'user',
        'ask_game',
        'ask_price',
        'pixiv',
        'search_by_picture',
        'search_by_user'
    ],
    transitions=[
        {
            'trigger': 'go_back',
            'source': [
                'ask_game',
                'ask_price',
                'pixiv',
                'search_by_picture',
                'search_by_user'
            ],
            'dest': 'user'
        },
        {
            'trigger': 'recommend',
            'source': 'user',
            'dest': 'ask_game',
            'conditions': 'is_going_to_ask_game'
        },
        {
            'trigger': 'about_price',
            'source': 'ask_game',
            'dest': 'ask_price',
            'conditions': 'is_going_to_ask_price'
        },
        {
            'trigger': 'search',
            'source': 'user',
            'dest': 'pixiv',
            'conditions': 'is_going_to_pixiv'
        },
        {
            'trigger': 'another_question',
            'source': 'ask_price',
            'dest': 'ask_game',
            'conditions': 'is_return_to_ask_game'
        },
        {
            'trigger': 'picture',
            'source': 'pixiv',
            'dest': 'search_by_picture',
            'conditions': 'is_search_by_picture'
        },
        {
            'trigger': 'user',
            'source': 'pixiv',
            'dest': 'search_by_user',
            'conditions': 'is_search_by_user'
        },
        {
            'trigger': 'research',
            'source': [
                'search_by_picture',
                'search_by_user'
            ],
            'dest': 'pixiv',
        }
    ],
    initial='user',
    auto_transitions=False,
    show_conditions=True,
)

cookies = {}
def init_cookies():
    f=open(r'cookies.txt','r')
    for line in f.read().split(';'): 
        name,value=line.strip().split('=',1)
        cookies[name]=value


@route("/webhook", method="GET")
def setup_webhook():
    mode = request.GET.get("hub.mode")
    token = request.GET.get("hub.verify_token")
    challenge = request.GET.get("hub.challenge")

    print(token)
    print(VERIFY_TOKEN)
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK_VERIFIED")
        return challenge

    else:
        abort(403)

def get_state():
    return machine.state

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
        'referer': 'https://www.pixiv.net/'
    }


@route("/webhook", method="POST")
def webhook_handler():
    body = request.json
    print('\nFSM STATE: ' + machine.state)
    print('REQUEST BODY: ')
    print(body)

    global game_type
    if body['object'] == "page":
        event = body['entry'][0]['messaging'][0]
        if 'message' in event and 'nlp' in event['message']:
            understand = False
            if get_state() == 'user':
                if 'greetings' in event['message']['nlp']['entities']:
                    understand = True
                    sender_id = event['sender']['id']
                    responese = send_text_message(sender_id, "hello, what can I do for you?")
                else:
                    machine.recommend(event)
                    machine.search(event)
                if understand == False and get_state() == 'user':
                    sender_id = event['sender']['id']
                    responese = send_text_message(sender_id, "I don't understand what you say")
            elif get_state() == 'ask_game':
                machine.about_price(event)
            elif get_state() == 'ask_price':
                machine.another_question(event)
            elif get_state() == 'pixiv':
                machine.picture(event)
                machine.user(event)
            elif get_state() == 'search_by_picture' and event['message']['text'] != 'picture':
                #url = "https://www.pixiv.net/search.php?word=" + event['message']['text']
                url = "https://imgur.com/search?q=" + event['message']['text']
                re = requests.get(url, headers=headers)
                #print(re.html())
                sender_id = event['sender']['id']
                soup = BeautifulSoup(re.text, 'html.parser')
                count = 0
                tag = soup.find_all('img')
                for src in tag:
                    count = count + 1
                    if count <= 5:
                        send_image_message(sender_id, 'https:' + src.get('src'))
                #print("fuck'fuck'fuck".split("'"))
                #print(print(soup(id="js-mount-point-search-result-list")[0].get('data-items')))
                #data = json.loads(soup(id="js-mount-point-search-result-list")[0].get('data-items'))
#                for url in data:
#                    count = count + 1
#                    if count <= 1:
#                        send_image_message(sender_id, url['url'])
#                    else:
#                        break
                machine.research(event)
            elif get_state() == 'search_by_user':
                #url = "https://www.pixiv.net/search_user.php?s_mode=s_usr&nick=" + event['message']['text']
                url = "https://imgur.com/search?q=" + event['message']['text']
                re = requests.get(url, headers=headers)
                print(re.text)
                machine.research(event)

            
            if 'bye' in event['message']['nlp']['entities'] and machine.state != 'user':
                sender_id = event['sender']['id']
                responese = send_text_message(sender_id, "wish you have a nice day")
                machine.go_back(event)


        #if event.get("message"):
        #    text = event['message']['text']
        #    print(text.lower())
        #    if text.lower() == 'game':
        #        machine.recommend(event)
        return 'OK'


@route('/show-fsm', methods=['GET'])
def show_fsm():
    machine.get_graph().draw('fsm.png', prog='dot', format='png')
    return static_file('fsm.png', root='./', mimetype='image/png')


if __name__ == "__main__":
    run(host="0.0.0.0", port=PORT, debug=True, reloader=True)
