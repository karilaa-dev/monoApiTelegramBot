import base64
from json import loads as jloads
from time import time, sleep
from datetime import datetime
from requests import get


#Закодировать в b64
def b64encode(text):
    result = base64.b64encode(text.encode("ascii"))
    return result.decode("ascii")

#Разкодировать из b64
def b64decode(text):
    result = base64.b64decode(text.encode("ascii"))
    return result.decode("ascii")

#Визуальный разделитель для денег
def convert(bal):
    if len(bal) >= 3:
        money = bal[:-2]+'.'+bal[-2:]
    elif len(bal) == 2:
        money = '0.'+bal[-2:]
    elif len(bal) == 1:
        money = '0.0'+bal[-2:]
    return money

#Текущее время
def timenow():
    return datetime.today().strftime("%B %d %H:%M:%S.%f")

#Унать время в UNIX
def tCurrent():
    return int(time())

#Кешированый ответ
def balance(api):
    osn_res, alr_res = str(), str()
    for numb in range (0, len(api["accounts"])):
        bal = str(api["accounts"][numb]["balance"])
        btype = api["accounts"][numb]["type"]
        if api["accounts"][numb]["currencyCode"] == 980 and btype != 'white' and btype != 'fop':
            osn_res += str(f'<b>{btype.capitalize()}</b> <code>{convert(bal)}</code>\n')
    for numb in range (0, len(api["accounts"])):
        bal = str(api["accounts"][numb]["balance"])
        btype = api["accounts"][numb]["type"]
        if btype == 'white':
            osn_res += str(f'<b>{btype.capitalize()}</b> <code>{convert(bal)}</code>\n')
    for numb in range (0, len(api["accounts"])):
        bal = str(api["accounts"][numb]["balance"])
        btype = api["accounts"][numb]["type"]
        if btype == 'fop':
            osn_res += str(f'<b>{btype.capitalize()}</b> <code>{convert(bal)}</code>\n')
    for numb in range (0, len(api["accounts"])):
        bal = str(api["accounts"][numb]["balance"])
        if api["accounts"][numb]["currencyCode"] == 840:
            alr_res += str(f'<b>USD</b> <code>{convert(bal)}</code>\n')
        elif api["accounts"][numb]["currencyCode"] == 978:
            alr_res += str(f'<b>EUR</b> <code>{convert(bal)}</code>\n')
        elif api["accounts"][numb]["currencyCode"] == 985:
            alr_res += str(f'<b>PLN</b> <code>{convert(bal)}</code>\n')
    return f'Основные счета:\n{osn_res}\nВалютные счета:\n{alr_res[:-1]}'

#Курс валют
def currency():
    with open("currency.json", "r") as f:
        cur = jloads(f.read())
    res = str('Покупка/Продажа')
    res += f'\n<b>USD:</b> <code>{cur[0]["rateBuy"]}/{cur[0]["rateSell"]}</code>'
    res += f'\n<b>EUR:</b> <code>{cur[1]["rateBuy"]}/{cur[1]["rateSell"]}</code>'
    res += f'\n<b>RUB:</b> <code>{cur[2]["rateBuy"]}/{cur[2]["rateSell"]}</code>'
    return res

#Запрос курса валют раз в час
def cureq():
    #Текущее время
    def timenow():
        return datetime.today().strftime("%B %d %H:%M:%S")
    #Бесконечный луп
    while True:
        #Запрос курсов
        req = get("https://api.monobank.ua/bank/currency").text
        if "errorDescription" not in req:
        #Сохранение запроса
            cur = open("currency.json", "w")
            cur.write(req)
            cur.close()
            print(f'{timenow()}: Done')
        else:
        #Вывод ошибки при ошибке
            print(f'{timenow()}: Error')
        #Задержка 60 минут 
        sleep(3600)