from transitions.extensions import GraphMachine
import os
from utils import send_text_message
import requests

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(
            model=self,
            **machine_configs
        )

#    def is_going_to_state1(self, event):
#        if event.get("message"):
#            text = event['message']['text']
#            return text.lower() == 'go to state1'
#        return False

#    def on_exit_state1(self):
#        print('Leaving state1')

    def is_going_to_ask_game(self, event):
        if 'recommend_game' in event['message']['nlp']['entities']:
            return True
        return False

    def on_enter_ask_game(self, event):
        print("ask for recommend")
        sender_id = event['sender']['id']
        responese = send_text_message(sender_id, "what kind of game do you want?")

    game_type = 'none'

    def is_going_to_ask_price(self, event):
        global game_type
        if 'game_type' in event['message']['nlp']['entities']:
            game_type = event['message']['nlp']['entities']['game_type'][0]['value']
            return True
        return False
    
    def on_enter_ask_price(self, event):
        sender_id = event['sender']['id']
        responese = send_text_message(sender_id, "do you care about the price?")

    def is_going_to_pixiv(self, event):
        if 'pixiv' in event['message']['nlp']['entities']:
            return True
        return False

    def on_enter_pixiv(self, event):
        sender_id = event['sender']['id']
        responese = send_text_message(sender_id, "do you want to search by picture or user?")

    def is_return_to_ask_game(self, event):
        if 'boolean' in event['message']['nlp']['entities']:
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
            return True
        return False

    def is_search_by_picture(self, event):
        if 'search_type' in event['message']['nlp']['entities'] and event['message']['nlp']['entities']['search_type'][0]['value'] == "picture":
            return True
        return False

    def on_enter_search_by_picture(self, event):
        sender_id = event['sender']['id']
        responese = send_text_message(sender_id, "please enter your keyword")

    def is_search_by_user(self, event):
        if 'search_type' in event['message']['nlp']['entities'] and event['message']['nlp']['entities']['search_type'][0]['value'] == "user":
            return True
        return False

    def on_enter_search_by_user(self, event):
        sender_id = event['sender']['id']
        responese = send_text_message(sender_id, "please enter your keyword")
