from bottle import route, run, request, abort, static_file
import os
from fsm import TocMachine
from utils import send_text_message, send_message

VERIFY_TOKEN = os.environ.get("ACCESS_TOKEN")
machine = TocMachine(
    states=[
        'user',
        'ask_game',
        'ask_price',
        'pixiv'
    ],
    transitions=[
        {
            'trigger': 'go_back',
            'source': [
                'ask_game',
                'ask_price',
                'pixiv'
            ],
            'dest': 'user'
        },
        {
            'trigger': 'recommend',
            'source': 'user',
            'dest': 'ask_game'
        },
        {
            'trigger': 'about_price',
            'source': 'ask_game',
            'dest': 'ask_price'
        },
        {
            'trigger': 'search',
            'source': 'user',
            'dest': 'pixiv'
        },
        {
            'trigger': 'another_question',
            'source': 'ask_price',
            'dest': 'ask_game'
        }
    ],
    initial='user',
    auto_transitions=False,
    show_conditions=True,
)


@route("/webhook", method="GET")
def setup_webhook():
    mode = request.GET.get("hub.mode")
    token = request.GET.get("hub.verify_token")
    challenge = request.GET.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK_VERIFIED")
        return challenge

    else:
        abort(403)

game_type = 'fuck'

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
            if 'recommend_game' in event['message']['nlp']['entities'] and machine.state == 'user':
                machine.recommend(event)
            elif 'boolean' in event['message']['nlp']['entities'] and machine.state == 'ask_price':                                       #     ask for game v
                sender_id = event['sender']['id']
                if event['message']['nlp']['entities']['boolean'][0]['value'] == 'false':
                    if game_type == 'RPG':
                        sender_id = event['sender']['id']
                        responese = send_text_message(sender_id, "https://store.steampowered.com/app/292030/The_Witcher_3_Wild_Hunt/")
                    elif game_type == 'WuSha':
                        sender_id = event['sender']['id']
                        responese = send_text_message(sender_id, "https://store.steampowered.com/app/882790/_Fate_Seeker/")
                    elif game_type == 'action':
                        sender_id = event['sender']['id']
                        responese = send_text_message(sender_id, "https://store.steampowered.com/app/271590/Grand_Theft_Auto_V/")
                    elif game_type == 'metroidvania':
                        sender_id = event['sender']['id']
                        responese = send_text_message(sender_id, "https://store.steampowered.com/app/367520/Hollow_Knight/")
                    elif game_type == 'STG':
                        sender_id = event['sender']['id']
                        responese = send_text_message(sender_id, "https://store.steampowered.com/app/289070/Sid_Meiers_Civilization_VI/")
                    elif game_type == 'SLG':
                        sender_id = event['sender']['id']
                        responese = send_text_message(sender_id, "https://store.steampowered.com/app/255710/Cities_Skylines/")
                else:
                    responese = send_text_message(sender_id, "you are too young to play game")
                machine.another_question(event)                                                                                           #      ask for game ^
            elif 'pixiv' in event['message']['nlp']['entities'] and machine.state == 'user':
                machine.search(event)
            elif 'game_type' in event['message']['nlp']['entities'] and machine.state == 'ask_game':
                game_type = event['message']['nlp']['entities']['game_type'][0]['value']
                machine.about_price(event)
            elif 'gm_type' in event['message']['nlp']['entities'] and machine.state == 'pixiv':
                gm_type = event['message']['nlp']['entities']['gm_type'][0]['value']
                sender_id = event['sender']['id']
                if gm_type == 'ps4':
                    responese = send_message(sender_id, "ps4", "ps4")
                    responese = send_text_message(sender_id, "wish you have a nice day")
                elif gm_type == 'xbox one':
                    responese = send_text_message(sender_id, "wish you have a nice day")
                elif gm_type == 'switch':
                    responese = send_text_message(sender_id, "wish you have a nice day")
            elif 'greetings' in event['message']['nlp']['entities']:
                sender_id = event['sender']['id']
                responese = send_text_message(sender_id, "hello, what can I do for you?")
            elif 'bye' in event['message']['nlp']['entities'] and machine.state != 'user':
                sender_id = event['sender']['id']
                responese = send_text_message(sender_id, "wish you have a nice day")
                machine.go_back(event)
            elif machine.state == 'user':
                sender_id = event['sender']['id']
                responese = send_text_message(sender_id, "I don't understand what you say")
            else:
                sender_id = event['sender']['id']
                responese = send_text_message(sender_id, "you are away from the theme")

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
    show_fsm()
    run(host="localhost", port=5000, debug=True, reloader=True)
