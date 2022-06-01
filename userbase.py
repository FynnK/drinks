#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  1 09:06:07 2022

@author: fynn
"""

import json
import requests
from datetime import datetime

def timestamp():
    return datetime.today().strftime('%Y-%m-%d')



class User:
    def __init__(self, id, name,tid = None, tName = None):
        self.id = id
        self.tid = tid
        self.name = name
        self.tName = tName

    def __str__(self):
        return "name: " + str(self.name)+"\n  id: " + str(self.id) + "\n  tid: " + str(self.tid)
    
    def get_as_dict(self):
        return {'id': self.id, 'name': self.name, 'activated': True, 'tid': self.tid, 'tName': self.tName}      

    def set_telegramdata(self, tid, tName):
        self.tid = tid
        self.tName = tName


class Userbase:
    def __init__(self):
        self.users: list[User] = []
                     
    def get_users(self):
        return self.users
    
    def add_user(self, user):
        if(user.id in self.get_ids()):
            return print("Error, user id already taken")
        if(user.tid in self.get_tids() and user.tid != None):
            return print("Error, user tid already taken")
        self.users.append(user)
        
    def get_ids(self):
        list = []
        for user in self.users:
            list.append(user.id)
        return list
            
    def get_tids(self):
        list = []
        for user in self.users:
            list.append(user.tid)
        return list

    def get_names(self):
        list = []
        for user in self.users:
            list.append(user.name)
        return list
    
    def has_user(self, user):
        return user in self.get_users()
    
    def id_taken(self, id):
        return id in self.get_ids()
    
    def tid_taken(self, tid):
        return tid in self.get_tids()
  
    
    def user_from_id(self, id):
        if not (self.id_taken(id)):
            return print("Error, id not taken")
        return next(u for u in self.users if u.id == id)
        
    def user_from_tid(self, tid):
        if not (self.tid_taken(tid)):
            return print("Error, tid not taken")            
        return next(u for u in self.users if u.tid == tid)

    def user_from_name(self, name):
        if not name in self.get_names():
            return print("Error, name not taken")            
        return next(u for u in self.users if u.name == name)

    def add_user_from_json(self, json):
        for user in json:
            self.add_user(User(user['id'], user['tid'], user['name'], user['tName']))
    
    def load_json_from_path(self, path):
        users = json.load(open(path,"r"))
        self.add_user_from_json(users)

    def load_from_url(self,  secrets):
            r = requests.get(secrets['url']+'/api/projects/'+secrets['project']+'/members',auth=(secrets['project'],secrets['password']))
            u = json.loads(r.text)
            for user in u:
                if user['id'] not in self.get_ids():
                    self.add_user(User(user['id'], user['name']))

    def dump_json_to_path(self, path):
        file = open(path, "w")
        users = []
        for user in self.get_users():
            users.append(user.get_as_dict())
        json.dump(users, file)
        file.close()