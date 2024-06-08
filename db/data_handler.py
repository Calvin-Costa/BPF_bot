import json
import peewee

class DataHandler:
    def __init__(self):
        pass 

    @staticmethod
    async def load_tierlist():
        try:
            with open('db/users_tierlist.json','r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    @staticmethod
    async def save_tierlist(tierlist_data):
        with open('db/users_tierlist.json','w') as f:
            json.dump(tierlist_data, f)

    @staticmethod
    async def load_novels():
        try:
            with open('db/novels.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        
    @staticmethod    
    async def save_novels(novels):
        with open('db/novels.json', 'w') as f:
            json.dump(novels, f)