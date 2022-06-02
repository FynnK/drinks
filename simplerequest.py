from datetime import datetime
import numpy as numpy
import argparse
import requests
import logging
import json

def load_json_path(path):
    with open(path, "r") as f:
        return json.load(f)


def timestamp():
	return datetime.today().strftime('%Y-%m-%d')


url = 'http://193.196.37.221/api/projects/i4_drinks'
resp = requests.get(url+'/members',auth=('i4_drinks','gib'))
userIds=[]
userList = json.loads(resp.text)

print(userList)

users = load_json_path("userBase.json")
secrets = load_json_path("secrets.json")
db = load_json_path("priceDB.json")
url = secrets['url']

rechnung = load_json_path("Consumed.json")
for user in rechnung["Bewohner"]:
	payed_for = next(item for item in userList if item["name"] ==  user["Name"])["id"]
	for item in user["Items"]:
		amount = user["Items"][item]
		total = round(amount * next(thing for thing in db if thing["name"] ==  item)["price"], 2)
		myobj = {'date':timestamp(), 'what':item, 'payer':'1', 'payed_for':payed_for,'amount':total}
		print(myobj)
		if (total > 0.1):
		    r = requests.post(url+'/api/projects/'+secrets['project']+'/bills', data = myobj, auth=(secrets['project'],secrets['password']))

print(r.text)
