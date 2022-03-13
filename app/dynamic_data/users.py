import os
import re

from dotenv import load_dotenv

load_dotenv()


class User:
    DATA: list

    def values(self):
        return self.DATA

    def get_chat_ids(self):
        return [item['chat_id'] for item in self.DATA]


class Moderator(User):
    def __init__(self):
        self.DATA = []

        moderator_ids = os.getenv('MODERATOR_IDS', default=None)
        for chat_id in re.split(' +', moderator_ids):
            self.DATA.append({'chat_id': chat_id})
