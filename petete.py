import os
import datetime
import json
import openai as AI
from dotenv import load_dotenv
# from types import SimpleNamespac

from tinydb import TinyDB, Query

load_dotenv()

class DataStore:
    _instance = None
    _db = TinyDB('db-settings.json')

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(DataStore, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Initialization code here. Make sure it's idempotent.
        pass

    def insert_user(self, data):
        self._db.insert(data)

    def update(self, data, query):
        self._db.update(data, query)

    def remove(self, query):
        self._db.remove(query)

    def search(self, query):
        return self._db.search(query)

    def all(self):
        return self._db.all()

    def purge(self):
        self._db.purge()

    def count(self):
        return len(self._db)

    def close(self):
        self._db.close()

    def __del__(self):
        self._db.close()


class Soul:
    _instance = None
    _db = TinyDB('db-settings.json')

    def __new__(cls, org_id, project_id, secret_key):
        if not cls._instance:
            cls._instance = super(Soul, cls).__new__(cls)
            cls._instance.Org_ID = org_id
            cls._instance.Project_ID = project_id
            cls._instance.Secret_Key = secret_key
            # Initialize the AI client here to ensure it's only done once
            cls._instance.client = AI.OpenAI(organization=org_id, project=project_id, api_key=secret_key)
        return cls._instance

    def __init__(self, org_id, project_id, secret_key):
        # Initialization code here. Make sure it's idempotent.
        system = Query()
        if not self._db.search(system.chat_setting == 'default'):
            self._db.insert({'chat_setting':'default', 
                             'role':'system',
                             'content':'You are a helpful assistant.', 
                             'model':'gpt-3.5-turbo'})
        else:
            self._db.update({'role':'system',
                             'content':'You are a helpful assistant.', 
                             'model':'gpt-3.5-turbo'}, system.chat_setting == 'default')
        pass

    def chat(self, message, user_id):
        # Accessing client through self.client
        User = Query()
        if self._db.search(User.user_id == user_id):
            system = Query()
            settings= self._db.search(system.chat_setting == "default")[0]
            setting_content = settings['content']
            setting_model = settings['model']
            completion = self.client.chat.completions.create(
                model= setting_model,
                messages=[
                    {"role": "system", "content": setting_content},
                    {"role": "user", "content": message}
                ]
            )
            
            return completion.choices[0].message
        else:
            return "You are not allowed to interact with the bot"
        
    
    # Allow user to interact with the bot    
    def allow_user(self, user_id, user_name, user_firstname):
        
        Data = Query()
        db_user = self._db.search(Data.all(item_type = 'user').data.any == user_id)
        if not self._db.search(User.id == user.id):
            db_user = {'item_type': 'user', 'data': {'user_id': user_id, 'user_name': user_name, 'user_firstname': user_firstname, 'role': 'user'}, 'created_at': datetime.datetime.now(), 'updated_at': datetime.datetime.now()}
            self._db.insert(db_user)
            print(f'User {user} allowed to interact with the bot')
            return True
        return False
    
    # Disallow user to interact with the bot
    def disallow_user(self, user_id):
        User = Query()
        if self._db.search(User.user_id == user_id):
            self._db.remove(User.user_id == user_id)
            return True
        return False
    
    def list_users(self):
        User = Query()
        return self._db.search(User.role == 'user')