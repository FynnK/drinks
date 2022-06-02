import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from datetime import datetime
import argparse
import requests
import logging
import json
import userbase


def load_json_path(path):
    with open(path, "r") as f:
        return json.load(f)

secrets = load_json_path("secrets.json")
prices = load_json_path("prices.json")
db = load_json_path("priceDB.json")

ubase = userbase.Userbase()
ubase.load_from_url(secrets)
print(ubase.get_users())


for entry in db:
    prices[entry["name"]] = entry["price"]

url = secrets['url']

def timestamp():
	return datetime.today().strftime('%Y-%m-%d')



logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')



bot = telegram.Bot(token=secrets["botToken"])
updater = Updater(token=secrets["botToken"], use_context=True)

dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

l = []
for item in db:
   l.append(InlineKeyboardButton(item["name"], callback_data=item["name"]))

n = 3
buttonList = [l[i:i + n] for i in range(0, len(l), n)] 
buttonList.append([InlineKeyboardButton("Cancel", callback_data="cancel")])




class Bot:
    def run(self):
       
        start_handler = CommandHandler('start', self.start)
        setUserName_handler = CommandHandler('setUserName', self.register)
        checkBalance_handler = CommandHandler('checkBalance', self.checkBalance)
        message_handler = MessageHandler(Filters.text, self.message)

        dispatcher.add_handler(CallbackQueryHandler(self.button))
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(setUserName_handler)
        dispatcher.add_handler(checkBalance_handler)
        dispatcher.add_handler(message_handler)

        updater.start_polling()
        updater.idle()

    def message(self, update, context):
        if update.message.text in 'preise':
            preisMsg = ''
            for key in prices.keys():
                preisMsg+=key + ': '+str(prices[key])+' Euro \n'
            context.bot.send_message(chat_id=update.effective_chat.id, text=preisMsg)
        if update.message.text in 'wasser':
            payed_for = ubase.user_from_tid(update.message.from_user.id).id
            myobj = {'date':timestamp(), 'what':'wasser', 'payer':'1', 'payed_for':payed_for,'amount':prices["wasser"]}
            r = requests.post(url+'/api/projects/'+secrets['project']+'/bills', data = myobj, auth=(secrets['project'],secrets['password']))
            context.bot.send_message(chat_id=update.effective_chat.id, text="you just bought some watah")

    def checkBalance(self, update, context):
        r = requests.get(url+'/api/projects/'+secrets['project'], auth=(secrets['project'],secrets['password']))
        obj = json.loads(r.text)
        userName = next(item for item in users if item["tId"] ==  update.effective_chat.id)["name"]
        print(userName)
        balance = next(item for item in obj["members"] if item["name"] == userName)["balance"]
        balance = round(balance, 2)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Your current balance is: "+str(balance)+" Euro")
        print(obj["members"])



    def register(self, update, context):
        tid = update.message.from_user.id
        if len(context.args) != 2:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Username should be: 'RoomNumber Firstname' for example i416 Soma")
            return
        uname = context.args[0] + ' '+ context.args[1]
        ubase.user_from_name(uname).set_telegramdata(update.message.from_user.id,update.message.chat.first_name)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Username: "+uname+"  TelegramId: "+str(tid))
        ubase.dump_json_to_path("mybase.json")

    def setUserName(self, update, context):
        if len(context.args) != 2:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Username should be: 'RoomNumber Firstname' for example i416 Soma")
            return
        uname = context.args[0] + ' '+ context.args[1]
        curUser = next((item for item in users if item["name"] == uname), 'None')
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

    def start(self, update, context):
        if update.message.from_user.id not in ubase.get_tids():
                context.bot.send_message(chat_id=update.effective_chat.id, text='Hello '+update.message.chat.first_name+ ', please send me: /setUserName RoomNumber Username')
        else:
            """Sends a message with three inline buttons attached."""
        keyboard = buttonList

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Please choose:', reply_markup=reply_markup)

    def button(self, update, context):
        query = update.callback_query
        query.answer()
        if(query.data == "cancel"):
            query.edit_message_text(text=f"Cancelled")
        else:
            query.edit_message_text(text=f"Purchased 1: {query.data}")
            payed_for = ubase.user_from_tid(query.from_user.id).id
            myobj = {'date':timestamp(), 'what':query.data, 'payer':'34', 'payed_for':payed_for,'amount':prices[query.data]}
            r = requests.post(url+'/api/projects/'+secrets['project']+'/bills', data = myobj, auth=(secrets['project'],secrets['password']))
            context.bot.send_message(chat_id=update.effective_chat.id, text=r.text)






b = Bot()
b.run()
