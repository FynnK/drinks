import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime
import numpy as numpy
import argparse
import imutils
import cv2
import requests
import logging
import json




uBase = open("userBase.json", "r")
users = json.load(uBase)
uBase.close()

secretsFile = open("secrets.json", "r")
secrets = json.load(secretsFile)
secretsFile.close()

userTIds = []
for user in users:
	userTIds.append(user.get('tId'))


url = secrets['url']

def timestamp():
	return datetime.today().strftime('%Y-%m-%d')


prices ={'wasser':0.3, 'mate':0.5, 'bier':0.9}

bot = telegram.Bot(token=secrets["botToken"])
updater = Updater(token=secrets["botToken"], use_context=True)

dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)




def message(update, context):
	if update.message.text in 'preise':
		preisMsg = ''
		for key in prices.keys():
			preisMsg+=key + ': '+str(prices[key])+' Euro \n'
		context.bot.send_message(chat_id=update.effective_chat.id, text=preisMsg)
	if update.message.text in 'wasser':
		payed_for = next(item for item in users if item["tId"] == update.message.from_user.id)["id"]

		myobj = {'date':timestamp(), 'what':'wasser', 'payer':'1', 'payed_for':payed_for,'amount':prices["wasser"]}
		r = requests.post(url+'/api/projects/'+secrets['project']+'/bills', data = myobj, auth=(secrets['project'],secrets['password']))
		context.bot.send_message(chat_id=update.effective_chat.id, text="you just bought some watah")



def setUserName(update, context):
	if len(context.args) != 2:
		 context.bot.send_message(chat_id=update.effective_chat.id, text="Username should be: 'RoomNumber Firstname' for example i416 Soma")
		 return
	uname = context.args[0] + ' '+ context.args[1]
	curUser = next((item for item in users if item["name"] == uname), 'none')
	if type(curUser) is type(''):
		 context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid user, please register in ihatemoney("+secrets["url"]+") or check Spelling")
		 return
	if curUser["tId"] == -1:
		curUser["tId"] = update.message.from_user.id
		curUser["tName"] = update.message.chat.first_name
	else:
		context.bot.send_message(chat_id=update.effective_chat.id, text="error")
		return

	context.bot.send_message(chat_id=update.effective_chat.id, text="Username: "+uname+"  TelegramId: "+str(curUser["tId"]))
	uBase = open("userBase.json", "w")
	json.dump(users, uBase)
	uBase.close()



def start(update, context):
	if update.message.from_user.id not in userTIds:
			context.bot.send_message(chat_id=update.effective_chat.id, text='Hello '+update.message.chat.first_name+ ', please send me: /setUserName RoomNumber Username')






start_handler = CommandHandler('start', start)
setUserName_handler = CommandHandler('setUserName', setUserName)
message_handler = MessageHandler(Filters.text, message)


dispatcher.add_handler(start_handler)
dispatcher.add_handler(setUserName_handler)
dispatcher.add_handler(message_handler)


updater.start_polling()
updater.idle()
