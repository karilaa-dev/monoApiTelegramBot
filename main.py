from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from os import path
from re import match
from requests import get as rget
from configparser import ConfigParser as configparser
from tinydb import TinyDB, Query
from pprint import pprint

#Импорт команд
from commands import *
#Импорт клавиатур
from keyboards import *

#Загрузка базы данных
db = TinyDB('db.json')
find = Query()

#Загрузка конфига
config = configparser()
config.read("config.ini")

#Загрузка id админа
admin_id = int(config["MonoApi"]["admin"])

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

bot = Bot(token=config["MonoApi"]["token"])
dp = Dispatcher(bot, storage=MemoryStorage())

async def check_access(message):
    if any(db.search((find.id == message.chat.id))) is True:
        return True
    await message.answer('Вам сюда нельзя')
    return False

class token_opt(StatesGroup):
    main = State()
    change = State()

class opt(StatesGroup):
    add = State()
    reset = State()

@dp.message_handler(commands=['start'], state='*')
async def send_start(message: types.Message, state: FSMContext):
    if await check_access(message) is True:
        await state.finish()
        startMessage = '<b>Приветсвую</b>, вы запустили бота для работы с <b>Monobank open API</b>'
        if db.search((find.id == message.chat.id))[0]["api"] is None:
            startMessage += '\n<code>Вы не добавили токен, добавьте его через меню или с помощью кнопки</code>'
            keyb = add_token
        else:
            keyb = keyboard
        await message.answer(startMessage, parse_mode="HTML", reply_markup=keyb)

@dp.message_handler(filters.Text(equals=["назад"], ignore_case=True), state='*')
@dp.message_handler(commands=["stop", "cancel", "back"], state='*')
async def cancel(message: types.Message, state: FSMContext):
    if await check_access(message) is True:
        stateCurr = await state.storage.get_state(user=message.chat.id)
        if stateCurr == 'token_opt:change':
            keyb = keyboardToken
        elif stateCurr == 'token_opt:main':
            keyb = keyboardOpt
        else:
            keyb = keyboard
        await message.answer('Вы вернулись назад', reply_markup=keyb)
        await state.finish()

@dp.message_handler(filters.Text(equals='Переключить режим откладки', ignore_case=True))
@dp.message_handler(commands=['debug'])
async def send_debug(message: types.Message):
    if await check_access(message) is True:
        user = db.search((find.id == message.chat.id))[0]
        if user["debug"] is True:
            db.update({'debug': False}, find.id == message.chat.id)
            res = 'Отладочная информация выключена'
        elif user["debug"] is False:
            db.update({'debug': True}, find.id == message.chat.id)
            res = 'Отладочная информация включена'
        await message.answer(res)

@dp.message_handler(filters.Text(equals='Настройки', ignore_case=True))
@dp.message_handler(commands=['options'])
async def send_options(message: types.Message):
    if await check_access(message) is True:
        await message.answer("Вы перешли в настройки", parse_mode="HTML", reply_markup=keyboardOpt)

@dp.message_handler(commands=['adduser'])
async def send_adduser(message: types.Message):
    if message.chat.id == admin_id:
        await message.reply("Введите id пользователя, или перешлите его сообщение", reply_markup=keyboardBack)
        await opt.add.set()

@dp.message_handler(state=opt.add)
async def send_adduser(message: types.Message, state: FSMContext):
    if message.forward_from is None:
        if message.text.isdigit():
            db.insert({'id': int(message.text), 'name': None, "delay": 0, "debug": False, "api": None, "req": None})
            await message.answer(f'Вы успешно добавили пользователя: <code>{message.text}</code>', parse_mode="HTML", reply_markup=keyboard)
        else:
            await message.answer(f'Вы неверно ввели id', parse_mode="HTML", reply_markup=keyboard)
    else:
        db.insert({'id': message.forward_from.id, 'name': None, "delay": 0, "debug": False, "api": None, "req": None})
        await message.answer(f'Вы успешно добавили пользователя: <code>{message.forward_from.id}</code>', parse_mode="HTML", reply_markup=keyboard)
    await state.finish()

@dp.message_handler(filters.Text(equals='Управление токеном', ignore_case=True))
@dp.message_handler(commands=['tokenmenu'])
async def tokenmenu(message: types.Message):
    if await check_access(message) is True:
        await message.answer('Вы перешли в меню управления токеном', reply_markup=keyboardToken)
        await token_opt.main.set()

@dp.message_handler(state=token_opt.main)
async def send_token_opt(message: types.Message, state: FSMContext):
    if message.text == "Просмотреть токен":
        dbreq = db.search((find.id == int(message.chat.id)))[0]["api"]
        if dbreq is not None:
            result = b64decode(dbreq)
        else:
            result = 'Токен отсутствует'
        await message.answer(f'<b>Ваш токен:</b>\n<code>{result}</code>', parse_mode="HTML")
        await token_opt.main.set()
    elif message.text == "Удалить токен":
        db.update({'api': None}, find.id == message.chat.id)
        await message.answer("Вы успешно удалили токен", reply_markup=keyboardToken)
        await token_opt.main.set()
    elif message.text == 'Изменить токен':
        await message.answer("Введите токен, взять вы его можете тут:\nhttps://api.monobank.ua/", reply_markup=keyboardBack)
        await token_opt.change.set()
    else:
        await token_opt.main.set()

@dp.callback_query_handler(lambda c: c.data == 'add_token')
async def send_token_change(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Введите токен, взять вы его можете тут:\nhttps://api.monobank.ua/", reply_markup=keyboardBack)
    await callback_query.answer()
    await token_opt.change.set()

@dp.message_handler(state=token_opt.change)
async def send_token_change(message: types.Message, state: FSMContext):
    if match("^[A-Za-z0-9_-]*$", message.text) is not None and len(message.text) == 44:
        headers = {'X-Token': message.text}
        tTest = jloads(rget("https://api.monobank.ua/personal/client-info",headers=headers).text)
        if "errorDescription" in tTest:
            if tTest["errorDescription"] in ["Missing one of required headers 'X-Token' or 'X-Key-Id'", "Unknown 'X-Token'"]:
                await message.answer('Ошибка, вы ввели неправильный токен')
            else:
                db.update({'api': b64encode(message.text)}, find.id == message.chat.id)
                await message.answer('Вы успешно изменили токен', reply_markup=keyboard)
        else:
            db.update({'api': b64encode(message.text)}, find.id == message.chat.id)
            db.update({'name': tTest["name"]}, find.id == message.chat.id)
            await message.answer('Вы успешно изменили токен', reply_markup=keyboard)
            await state.finish()
    else:
        await message.answer('Ошибка, вы ввели неправильный токен')
        await token_opt.change.set()

@dp.message_handler(filters.Text(equals='Сбросить настройки', ignore_case=True))
@dp.message_handler(commands=['reset'])
async def send_reset(message: types.Message):
    if await check_access(message) is True:
        await message.answer("Вы уверены что ходите сбросить настройки бота?", reply_markup=reset_buttons)

@dp.callback_query_handler(lambda c: c.data.startswith('reset'))
async def inline_reset(callback_query: types.CallbackQuery):
    if callback_query.data == 'reset_accept':
        db.update({'api': None, 'req': None, 'name': None}, find.id == callback_query.from_user.id)
        res = 'Вы успешно сбросили настройки'
    else:
        res = 'Вы отменили сброс настроек'
    msg_id = callback_query.message.message_id
    cht_id = callback_query.from_user.id
    await bot.edit_message_text(message_id=msg_id, chat_id=cht_id, text=res)
    await callback_query.answer()

@dp.message_handler(filters.Text(equals='Курс валют', ignore_case=True))
@dp.message_handler(commands=['currency'])
async def send_currency(message: types.Message):
    cur = await currency()
    await message.answer(cur, parse_mode="HTML")

@dp.message_handler(filters.Text(equals='Баланс', ignore_case=True))
@dp.message_handler(commands=['balance'])
async def send_balance(message: types.Message):
    if await check_access(message) is True:
        user = db.search((find.id == message.chat.id))[0]
        if user["api"] is None:
            await message.answer('Вы не добавили токен, добавте его через меню')
        else:
            headers = {'X-Token': b64decode(user["api"])}
            delay = user["delay"]
            timenow =  tCurrent()
            edit_t = False
            if delay < timenow:
                msg = await message.answer('<code>Выполняется запрос</code>', parse_mode='HTML')
                edit_t = True
                api = rget("https://api.monobank.ua/personal/client-info",headers=headers).json()
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
            elif delay >= timenow and user["req"] is not None:
                result = "cache\n"
                api = user["req"]
            else:
                result = "no cache\n"
                api = {"accounts": [{"currencyCode": 980, "balance": 0, "type": "black"}]}
            if user["debug"] is False:
                result = str()
            bal = await balance(api)
            if edit_t == True:
                await msg.edit_text(f'<code>{result}</code>{bal}', parse_mode="HTML")
            else:
                await message.answer(f'<code>{result}</code>{bal}', parse_mode="HTML")

if __name__ == '__main__':

    #Запуск бота
    print("Бот запущен")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(cureq)
    scheduler.add_job(cureq, "interval", seconds=3600)
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)