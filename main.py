import requests, json, time, telebot, re
from configparser import ConfigParser as configparser
from tinydb import TinyDB, Query
from commands import *
from keyboards import *

config = configparser()  # создаём объекта парсера
config.read("config.ini")

db = TinyDB('db.json')
find = Query()

bot = telebot.TeleBot(config["MonoApi"]["token"])

admin_id = config["MonoApi"]["admin"]

print("Бот запущен")

@bot.message_handler(content_types=['text'])
def send_text(message):
    bot.register_next_step_handler(message, send_text)
    text = message.text
    if message.chat.id == 217362163 or any(db.search((find.id == message.chat.id))) == True:
        if text == '/start':
            startMessage = '<b>Приветсвую</b>, вы запустили бота для работы с <b>Monobank open API</b>'
            if db.search((find.id == message.chat.id))[0]["api"] == None:
                startMessage += '\n<code>Вы не добавили токен, добавьте его через меню</code>'
            bot.send_message(message.chat.id, startMessage, parse_mode="HTML", reply_markup=keyboard)
        elif text == 'Настройки':
            bot.send_message(message.chat.id, "Вы перешли в настройки", parse_mode="HTML", reply_markup=keyboardOpt)
        elif text == '/adduser':
            bot.send_message(message.chat.id, "Введите id пользователя", reply_markup=keyboardBack)
            bot.register_next_step_handler(message, adduser)
        elif text == 'Управление токеном':
            bot.send_message(message.chat.id, "Вы перешли в меню управления токеном", reply_markup=keyboardToken)
        elif text == '/changetoken' or text == 'Изменить токен':
            bot.send_message(message.chat.id, "Введите токен, взять вы его можете тут:\nhttps://api.monobank.ua/", reply_markup=keyboardBack)
            bot.register_next_step_handler(message, changetoken)
        elif text == '/deltoken' or text == 'Удалить токен':
            bot.send_message(message.chat.id, "Вы успешно удалили токен", reply_markup=keyboardToken)
            db.update({'api': None}, find.id == message.chat.id)
        elif text == '/reset' or text == 'Сбросить настройки':
            bot.send_message(message.chat.id, "Вы уверены что ходите сбросить настройки бота?", reply_markup=keyboardDelToken)
            bot.register_next_step_handler(message, reset)
        elif text == '/token' or text == 'Просмотреть токен':
            bot.send_message(message.chat.id, f'<b>Ваш токен:</b>\n<code>{db.search((find.id == int(message.chat.id)))[0]["api"]}</code>', parse_mode="HTML")
        elif text == 'Назад':
            bot.send_message(message.chat.id, "Переход в главное меню", reply_markup=keyboard)  
        elif text == '/balance' or text == 'Баланс':
            user = db.search((find.id == message.chat.id))[0]
            headers = {'X-Token': user["api"]}
            delay = user["delay"]
            if user["api"] == None:
                bot.send_message(message.chat.id, 'Вы не добавили токен, добавте его через меню', reply_markup=keyboard)
            else:
                if delay < tCurrent():
                    api = json.loads(requests.get("https://api.monobank.ua/personal/client-info",headers=headers).text)
                    if "errorDescription" in api:
                        if user["req"] == None:
                            result = "no cache\n"
                            api = {"accounts": [{"currencyCode": 980, "balance": 0, "type": "black"}]}
                        elif user["req"] != None:
                            result = "request error, using cache\n"
                            api = user["req"]
                    else:
                        if user["name"] == None:
                            db.update({'name': api["name"]}, find.id == message.chat.id)
                        result = "new\n"
                        db.update({'req': api}, find.id == message.chat.id)
                    db.update({'delay': tCurrent()+30}, find.id == message.chat.id)
                elif delay >= tCurrent() and user["req"] != None:
                    result = "cache\n"
                    api = user["req"]
                else:
                    result = "no cache\n"
                    api = {"accounts": [{"currencyCode": 980, "balance": 0, "type": "black"}]}
                bot.send_message(message.chat.id, f'<code>{result}</code>{balance(api)}', parse_mode="HTML", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Вас сюда нельзя')

def adduser(message):
    if message.text != 'Назад':
        if message.forward_from == None:
            db.insert({'id': int(message.text), 'name': None, "delay": 0, "api": None, "req": None})
            bot.send_message(message.chat.id, f'Вы успешно добавили пользователя: <code>{message.text}</code>', parse_mode="HTML", reply_markup=keyboard)
        else:
            db.insert({'id': message.forward_from.id, 'name': None, "delay": 0, "api": None, "req": None})
            bot.send_message(message.chat.id, f'Вы успешно добавили пользователя: <code>{message.forward_from.id}</code>', parse_mode="HTML", reply_markup=keyboard)
def changetoken(message):
    if message.text != 'Назад':
        if re.match("^[A-Za-z0-9_-]*$", message.text) != None and len(message.text) == 44:
            headers = {'X-Token': message.text}
            tTest = json.loads(requests.get("https://api.monobank.ua/personal/client-info",headers=headers).text)
            if "errorDescription" in tTest:
                if tTest["errorDescription"] == "Missing one of required headers 'X-Token' or 'X-Key-Id'" or tTest["errorDescription"] == "Unknown 'X-Token'":
                    bot.send_message(message.chat.id, 'Ошибка, вы ввели неправильный токен', reply_markup=keyboardOpt)
                else:
                    db.update({'api': message.text}, find.id == message.chat.id)
                    bot.send_message(message.chat.id, 'Вы успешно изменили токен', reply_markup=keyboard)
            else:
                db.update({'api': message.text}, find.id == message.chat.id)
                db.update({'name': tTest["name"]}, find.id == message.chat.id)
                bot.send_message(message.chat.id, 'Вы успешно изменили токен', reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, 'Ошибка, вы ввели неправильный токен', reply_markup=keyboardOpt)
def reset(message):
    if message.text == 'Нет':
        bot.send_message(message.chat.id, 'Вы перешли в настройки', reply_markup=keyboardOpt)
    elif message.text == 'Да':
        db.update({'api': None}, find.id == message.chat.id)
        db.update({'req': None}, find.id == message.chat.id)
        db.update({'name': None}, find.id == message.chat.id)
        bot.send_message(message.chat.id, 'Вы сбросили настройки', reply_markup=keyboard)
bot.polling(none_stop=True)