from telebot import Telebot as telebot
from os import path
from re import match
from requests import ger as rget
from json import loads as jloads
from configparser import ConfigParser as configparser
from tinydb import TinyDB, Query
from multiprocessing import Process

#Импорт команд
from commands import *
#Импорт клавиатур
from keyboards import *

#Загрузка конфига
config = configparser()
config.read("config.ini")

bot = telebot(config["MonoApi"]["token"])

#Основной блок бота
@bot.message_handler(content_types=['text'])
def send_text(message):
    bot.register_next_step_handler(message, send_text)
    text = message.text
    #Проверка доступа
    if message.chat.id == admin_id or any(db.search((find.id == message.chat.id))) is True:
        if text == '/start':
            startMessage = '<b>Приветсвую</b>, вы запустили бота для работы с <b>Monobank open API</b>'
            if db.search((find.id == message.chat.id))[0]["api"] is None:
                startMessage += '\n<code>Вы не добавили токен, добавьте его через меню</code>'
            bot.send_message(message.chat.id, startMessage, parse_mode="HTML", reply_markup=keyboard)
        #Настройки
        elif text == 'Настройки' or text == '/options':
            bot.send_message(message.chat.id, "Вы перешли в настройки", parse_mode="HTML", reply_markup=keyboardOpt)
        #Добавление пользователя
        elif text == '/adduser' and message.chat.id == admin_id:
            bot.send_message(message.chat.id, "Введите id пользователя, или перешлите его сообщение", reply_markup=keyboardBack)
            bot.register_next_step_handler(message, adduser)
        #Переход в меню "Управление токеном"
        elif text == 'Управление токеном' or text == '/tokenmenu':
            bot.send_message(message.chat.id, "Вы перешли в меню управления токеном", reply_markup=keyboardToken)
        #Изменить токен
        elif text == 'Изменить токен' or text == '/changetoken':
            bot.send_message(message.chat.id, "Введите токен, взять вы его можете тут:\nhttps://api.monobank.ua/", reply_markup=keyboardBack)
            bot.register_next_step_handler(message, changetoken)
        #Удалить токен
        elif text == 'Удалить токен' or text == '/deltoken':
            bot.send_message(message.chat.id, "Вы успешно удалили токен", reply_markup=keyboardToken)
            db.update({'api': None}, find.id == message.chat.id)
        #Сбросить все настройки
        elif text == 'Сбросить настройки' or text == '/reset':
            bot.send_message(message.chat.id, "Вы уверены что ходите сбросить настройки бота?", reply_markup=keyboardDelToken)
            bot.register_next_step_handler(message, reset)
        #Посмотреть токен
        elif text == 'Просмотреть токен' or text == '/token':
            dbreq = db.search((find.id == int(message.chat.id)))[0]["api"]
            if dbreq is not None:
                result = b64decode(dbreq)
            else:
                result = 'Токен отсутствует'
            bot.send_message(message.chat.id, f'<b>Ваш токен:</b>\n<code>{result}</code>', parse_mode="HTML")
        #Назад в главное меню
        elif text == 'Назад':
            bot.send_message(message.chat.id, "Переход в главное меню", reply_markup=keyboard)
        #Курс валют
        elif text == 'Курс валют' or text == '/currency':
            bot.send_message(message.chat.id, currency(), parse_mode="HTML")
        elif text == 'Переключить режим откладки' or text == '/debug':
            user = db.search((find.id == message.chat.id))[0]
            if user["debug"] is True:
                db.update({'debug': False}, find.id == message.chat.id)
                res = 'Отладочная информация выключена'
            elif user["debug"] is False:
                db.update({'debug': True}, find.id == message.chat.id)
                res = 'Отладочная информация включена'
            bot.send_message(message.chat.id, res)
        #Баланс
        elif text == 'Баланс' or text == '/balance' :
            user = db.search((find.id == message.chat.id))[0]
            if user["api"] is None:
                bot.send_message(message.chat.id, 'Вы не добавили токен, добавте его через меню', reply_markup=keyboard)
            else:
                headers = {'X-Token': b64decode(user["api"])}
                delay = user["delay"]
                if delay < tCurrent():
                    api = jloads(rget("https://api.monobank.ua/personal/client-info",headers=headers).text)
                    if "errorDescription" in api:
                        if user["req"] is None:
                            result = "no cache\n"
                            api = {"accounts": [{"currencyCode": 980, "balance": 0, "type": "black"}]}
                        elif user["req"] is not None:
                            result = "request error, using cache\n"
                            api = user["req"]
                    else:
                        if user["name"] is None:
                            db.update({'name': api["name"]}, find.id == message.chat.id)
                        result = "new\n"
                        db.update({'req': api}, find.id == message.chat.id)
                    db.update({'delay': tCurrent()+30}, find.id == message.chat.id)
                elif delay >= tCurrent() and user["req"] is not None:
                    result = "cache\n"
                    api = user["req"]
                else:
                    result = "no cache\n"
                    api = {"accounts": [{"currencyCode": 980, "balance": 0, "type": "black"}]}
                if user["debug"] is not True:
                    result = str()
                bot.send_message(message.chat.id, f'<code>{result}</code>{balance(api)}', parse_mode="HTML", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Вам сюда нельзя')

def adduser(message):
    if message.text != 'Назад':
        if message.forward_from is None:
            db.insert({'id': int(message.text), 'name': None, "delay": 0, "debug": False, "api": None, "req": None})
            bot.send_message(message.chat.id, f'Вы успешно добавили пользователя: <code>{message.text}</code>', parse_mode="HTML", reply_markup=keyboard)
        else:
            db.insert({'id': message.forward_from.id, 'name': None, "delay": 0, "debug": False, "api": None, "req": None})
            bot.send_message(message.chat.id, f'Вы успешно добавили пользователя: <code>{message.forward_from.id}</code>', parse_mode="HTML", reply_markup=keyboard)
def changetoken(message):
    if message.text != 'Назад':
        if match("^[A-Za-z0-9_-]*$", message.text) is not None and len(message.text) == 44:
            headers = {'X-Token': message.text}
            tTest = jloads(rget("https://api.monobank.ua/personal/client-info",headers=headers).text)
            if "errorDescription" in tTest:
                if tTest["errorDescription"] == "Missing one of required headers 'X-Token' or 'X-Key-Id'" or tTest["errorDescription"] == "Unknown 'X-Token'":
                    bot.send_message(message.chat.id, 'Ошибка, вы ввели неправильный токен', reply_markup=keyboardOpt)
                else:
                    db.update({'api': b64encode(message.text)}, find.id == message.chat.id)
                    bot.send_message(message.chat.id, 'Вы успешно изменили токен', reply_markup=keyboard)
            else:
                db.update({'api': b64encode(message.text)}, find.id == message.chat.id)
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

if __name__ == '__main__':

    #Загрузка id админа
    admin_id = int(config["MonoApi"]["admin"])

    #Загрузка базы данных
    db = TinyDB('db.json')
    find = Query()

    #Проверка существования config.ini
    if not path.exists('config.ini'):
        print("Не найден конфиг файл!!!")
        token_req = input("Введите токен бота:\n> ")
        admin_req = input("Введите айди админа:\n> ")
        config['MonoApi'] = {'token': token_req, 'admin': admin_req}
        config.write(open('config.ini', 'w'))
        print("Создан файл с конфигом, при нужде его можно подправить вручную.")

    #Проверка существования db.json
    if db.search((find.id == admin_id)) == []:
        db.insert({'id': int(admin_id), 'name': None, "delay": 0, "debug": True, "api": None, "req": None})
        print("Создана база данных с доступом для админа.\n")

    #Запуск бота
    print("Бот запущен")

    cur = Process(target=cureq).start()
    bot.polling(none_stop=True)