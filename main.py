import telebot
from datetime import date
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

bot = telebot.TeleBot('6208096452:AAGj5-rPFgJx2xE19ZG99J1ABdCFJchpjKA')

uri = "mongodb+srv://aiekeu:wf0WgIGk9VTVZido@cluster0.9vrxv0m.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

mydb = client["main"]
mycol = mydb["user"]

min = 5
loo = 30
max = 50


def isNewUser(id):
    x = mycol.find_one({}, {"id": id})
    if not x: return True
    return False

def createUser(id, nick):
    mydict = {"name": nick, "id": id, "min": 5, "100%": 30, "max": 50, "todayspage": 0, "totalpage": 0, "minscore" : 0,
              "100%score" : 0, "maxscore" : 0}
    x = mycol.insert_one(mydict)

def printMin(message):
    user = mycol.find_one({"id": message.from_user.id})
    text = f'min - {user["min"]}' + '\n' + f'100% - {user["100%"]}' + '\n' + f'max - {user["max"]}'
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['start'])
def main(message):
    if (isNewUser(message.from_user.id)):
        createUser(message.from_user.id, message.from_user.first_name)
        text = 'your profile has been succesfully created \n' + f'your default setting are:'
        bot.reply_to(message, text)
        printMin(message)
        bot.send_message(message.chat.id, f'if you want to change it type /upgrademin')
    else:
        bot.send_message(message.chat.id, f"You're authorized user")


@bot.message_handler(commands=['myMin'])
def main(message):
    user = mycol.find_one({"id": message.from_user.id})
    if not user:
        bot.send_message(message.chat.id, f"you're not authorized user type /start to authorize")
    else:
        printMin(message)


@bot.message_handler(commands=['midnight'])
def main(message):
    for x in mycol.find():
        if x['todayspage'] >= x['max']:
            myquery = {"id": x['id']}
            newvalues = {"$set": {"maxscore": int(x['maxscore']) + 1}}
            mycol.update_one(myquery, newvalues)
        elif x['todayspage'] >= x['100%']:
            myquery = {"id": x['id']}
            newvalues = {"$set": {"100%score": x['100%score'] + 1}}
            mycol.update_one(myquery, newvalues)
        elif x['todayspage'] >= x['min']:
            myquery = {"id": x['id']}
            newvalues = {"$set": {"minscore": x['minscore'] + 1}}
            mycol.update_one(myquery, newvalues)
        myquery = {"id": x['id']}
        newvalues = {"$set": {"totalpage": x['totalpage'] + x['todayspage'], "todayspage": 0}}
        mycol.update_one(myquery, newvalues)
    text = "Current scoreboard: \n \n"
    for x in mycol.find():
        text += x['name'] + ": " + str(x['minscore'] + x['100%score'] * 5 + x['maxscore'] * 10) + "\n"
    bot.send_message(-1001562170594, text)


@bot.message_handler(commands=['mystats'])
def mystats(message):
    user = mycol.find_one({"id": message.from_user.id})
    if not user:
        bot.send_message(message.chat.id, f"you're not authorized user type /start to authorize")
    else:
        text = user['name'] + '👤' + '\n' + '\n' + "minscore: " + str(user['minscore'])
        text += '\n' "100% score: " + str(user['100%score'])
        text += '\n' "max score: " + str(user['maxscore'])
        text += '\n' + '\n' "total pages: " + str(user['totalpage'])
        bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['changenick'])
def main(message):
    bot.send_message(message.chat.id, 'new nickname?')
    bot.register_next_step_handler(message, get_nick)


def get_nick(message):
    user = mycol.find_one({"id": message.from_user.id})
    if not user:
        bot.send_message(message.chat.id, f"you're not authorized user type /start to authorize")
    else:
        myquery = {"id": message.from_user.id}
        newvalues = {"$set": {"name": message.text}}
        mycol.update_one(myquery, newvalues)
        bot.send_message(message.chat.id, f'привет {message.text}')



@bot.message_handler(commands=['upgrademin'])
def upgrademin(message):
    user = mycol.find_one({"id": message.from_user.id})
    if not user:
        bot.send_message(message.chat.id, f"you're not authorized user type /start to authorize")
    else:
        bot.send_message(message.chat.id, 'min:')
        bot.register_next_step_handler(message, get_loo)


def get_loo(message):
    global min
    try:
        min = int(message.text)
    except Exception:
        bot.send_message(message.chat.id, 'Цифрами, пожалуйста')
    bot.send_message(message.chat.id, '100%:')
    bot.register_next_step_handler(message, get_max)


def get_max(message):
    global loo
    try:
        loo = int(message.text)
    except Exception:
        bot.send_message(message.chat.id, 'Цифрами, пожалуйста')
    bot.send_message(message.chat.id, 'max:')
    bot.register_next_step_handler(message, submit)


def submit(message):
    global min, loo, max
    try:
        max = int(message.text)
        myquery = {"id": message.from_user.id}
        newvalues = {"$set": {"min": min, "100%": loo, "max": max}}
        mycol.update_one(myquery, newvalues)
    except Exception:
        bot.send_message(message.chat.id, 'Цифрами, пожалуйста')
    printMin(message)
    bot.send_message(message.chat.id, 'Updated')


@bot.message_handler()
def parse(message):
    user = mycol.find_one({"id": message.from_user.id})
    if not user:
        bot.send_message(message.chat.id, f"you're not authorized user type /start to authorize")
    else:
        today = date.today()
        day = today.strftime("%d") + '.' + today.strftime("%m")
        text = message.text
        if (day == text.splitlines()[0]):
            if (len(text.splitlines()) == 2):
                try:
                    a = int(text.splitlines()[1])
                    myquery = {"id": message.from_user.id}
                    newvalues = {"$set": {"todayspage": a}}
                    mycol.update_one(myquery, newvalues)
                    bot.reply_to(message, 'интернет запомнил')
                except Exception:
                    bot.send_message(message.chat.id, 'Цифрами, пожалуйста')

bot.polling(none_stop=True)
