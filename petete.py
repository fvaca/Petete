import os
import json
import datetime
import openai as AI
from dotenv import load_dotenv


from tinydb import TinyDB, Query

load_dotenv()


class Soul:
    _instance = None
    _dbChats = TinyDB('./datastore/chats-records.json')    
    _dbUsers = TinyDB('./datastore/db-users.json')
    
    _dbGroupsChats = TinyDB('./datastore/groups-records.json')
    _dbGroupsSettings = TinyDB('./datastore/groups-settings.json')

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
        # system = Query()
        # if not self._dbSettings.search(system.chat_setting == 'default'):
        #     self._dbSettings.insert({'chat_setting':'default', 
        #                      'role':'system',
        #                      'content':'You are a helpful assistant.', 
        #                      'model':'gpt-3.5-turbo'})
        # else:
        #     self._dbSettings.update({'role':'system',
        #                      'content':'You are a helpful assistant.', 
        #                      'model':'gpt-3.5-turbo'}, system.chat_setting == 'default')
        pass

    def chat(self, message, user_id, is_group=False, group_id=None):
        # Accessing client through self.client       
        
        if self._dbGroupsSettings.search(Query().id == group_id) or self._dbUsers.search(Query().id == user_id):         
           
            model = 'gpt-3.5-turbo'
            if not is_group:
                model = self.get_user_model(user_id)
            else:
                model = self.get_group_model(group_id)
                
            completion = self.client.chat.completions.create(
                model= model,
                messages=self.create_chat_message(user_id, message, is_group, group_id))
            
            bot_message = completion.choices[0].message.content
                
            return bot_message
        else:
            return "You are not allowed to interact with the bot"

    
    def create_chat_message(self, user_id, message, is_group=False, group_id=None):
        
        behavior = self.get_user_behavior(user_id) if not is_group else self.get_group_behavior(group_id)
        messages = []
        messages.append({"role": 'system', "content": behavior})
        
        
        self.record_message(user_id, message, is_group, group_id)
        
        chats = Query()        
        chats = self._dbChats.search(chats.user_id == user_id) if not is_group else self._dbGroupsChats.search(chats.group_id == group_id)        
        for chat in chats:
            messages.append({"role": chat['role'], "content": chat['content']})        
        
        return messages

    def record_message(self, user_id, message, is_group, group_id):
        if message:
            if not is_group:
                self._dbChats.insert({'user_id': user_id, 
                                  'role': 'user', 
                                  'content': message, 
                                  'date_added': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            elif is_group:
                self._dbGroupsChats.insert({'group_id': group_id, 
                                  'role': 'user', 
                                  'content': message, 
                                  'date_added': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    
    def get_messages(self, user_id=None):
        
        if user_id:
            chats = Query()
            return self._dbChats.search(chats.user_id == user_id)
        else:
            return self._dbChats.all()     
    
    # Bot Management    
    def allow_user(self, user_id, username, user_firstname):
        User = Query()
        if not self._dbUsers.search(User.id == user_id):
            self._dbUsers.insert({'id': user_id, 
                                  'first_name': user_firstname, 
                                  'username': username, 
                                  'model':'gpt-3.5-turbo',
                                  'behavior':'Ere Petete, un personaje animado de origen argentino creado por el dibujante Manuel García Ferré, un pequeño pingüino que se hizo muy popular en los años 70 y 80 gracias a su participación en la televisión a través de segmentos cortos conocidos como "El Libro Gordo de Petete".',
                                  'date_added': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            return True
        return False
    def allow_group(self, group_id):
        Group = Query()
        if not self._dbGroupsSettings.search(Group.id == group_id):
            self._dbGroupsSettings.insert({'id': group_id,
                                  'model':'gpt-3.5-turbo',
                                  'behavior':'Ere Petete, un personaje animado de origen argentino creado por el dibujante Manuel García Ferré, un pequeño pingüino que se hizo muy popular en los años 70 y 80 gracias a su participación en la televisión a través de segmentos cortos conocidos como "El Libro Gordo de Petete".',
                                  'date_added': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            return True
        return False
        
    # Behavior Management
    def get_user_behavior(self, user_id):
        User = Query()
        if self._dbUsers.search(User.id == user_id):
            return self._dbUsers.search(User.id == user_id)[0]['behavior']
        return None
    def get_group_behavior(self, group_id):
        Group = Query()
        if self._dbGroupsSettings.search(Group.group_id == group_id):
            return self._dbGroupsSettings.search(Group.group_id == group_id)[0]['behavior']
        return None
    def update_user_behavior(self, user_id, behavior):
        User = Query()
        if self._dbUsers.search(User.id == user_id):
            self._dbUsers.update({'behavior': behavior}, User.id == user_id)
            return True
        return False
    def update_group_behavior(self, group_id, behavior):
        Group = Query()
        if self._dbGroupsSettings.search(Group.group_id == group_id):
            self._dbGroupsSettings.update({'behavior': behavior}, Group.group_id == group_id)
            return True
        return False
    
    # Models management    
    def get_user_model(self, user_id):
        User = Query()
        usersearch = self._dbUsers.search(User.id == user_id)
        if usersearch:            
            return usersearch[0]['model']
        return None    
    def get_group_model(self, group_id):
        Group = Query()
        groupsearch = self._dbGroupsSettings.search(Group.group_id == group_id)
        if groupsearch:
            return groupsearch[0]['model']
        else:
            self._dbGroupsSettings.insert({'group_id': group_id, 
                                  'model':'gpt-3.5-turbo',
                                  'behavior':'Eres Petete, un personaje animado de origen argentino creado por el dibujante Manuel García Ferré, un pequeño pingüino que se hizo muy popular en los años 70 y 80 gracias a su participación en la televisión a través de segmentos cortos conocidos como "El Libro Gordo de Petete".',
                                  'date_added': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            return 'gpt-3.5-turbo'
    def update_user_model(self, user_id, model):
        User = Query()
        if self._dbUsers.search(User.id == user_id):
            self._dbUsers.update({'model': model}, User.id == user_id)
            return True
        return False 
    def update_group_model(self, group_id, model):
        Group = Query()
        if self._dbGroupsSettings.search(Group.group_id == group_id):
            self._dbGroupsSettings.update({'model': model}, Group.group_id == group_id)
            return True
        return False
    
   
    # Disallow user to interact with the bot
    def disallow_user(self, user_id):
        User = Query()
        if self._dbUsers.search(User.id == user_id):
            self._dbUsers.remove(User.id == user_id)
            return True
        return False
    
    def list_users(self):
        User = Query()
        return self._dbUsers.all()
    