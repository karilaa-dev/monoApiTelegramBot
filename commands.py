import time, base64, json

#Закодировать в b64
def b64encode(text):
    bytes = base64.b64encode(text.encode("ascii"))
    return bytes.decode("ascii")

#Разкодировать из b64
def b64decode(text):
    bytes = base64.b64decode(text.encode("ascii"))
    return bytes.decode("ascii")

#Визуальный разделитель для денег
def convert(bal):
    if len(bal) >= 3:
        money = bal[:-2]+'.'+bal[-2:]
        return money
    elif len(bal) == 2:
        money = '0.'+bal[-2:]
        return money
    elif len(bal) == 1:
        money = '0.0'+bal[-2:]
        return money

#Унать время в UNIX
def tCurrent():
    return int(time.time())

#Кешированый ответ
def balance(api):
    osn_res, alr_res = str(), str()
    for numb in range (0, len(api["accounts"])):
        bal = str(api["accounts"][numb]["balance"])
        type = api["accounts"][numb]["type"]
        if api["accounts"][numb]["currencyCode"] == 980 and type != 'white' and type != 'fop':
            osn_res += str(f'<b>{type.capitalize()}</b> <code>{convert(bal)}</code>\n')
    for numb in range (0, len(api["accounts"])):
        bal = str(api["accounts"][numb]["balance"])
        type = api["accounts"][numb]["type"]
        if type == 'white':
            osn_res += str(f'<b>{type.capitalize()}</b> <code>{convert(bal)}</code>\n')
    for numb in range (0, len(api["accounts"])):
        bal = str(api["accounts"][numb]["balance"])
        type = api["accounts"][numb]["type"]
        if type == 'fop':
            osn_res += str(f'<b>{type.capitalize()}</b> <code>{convert(bal)}</code>\n')
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
    f = open("currency.json", "r")
    cur = json.loads(f.read())
    f.close
    res = str('Покупка/Продажа')
    res += f'\n<b>USD:</b> <code>{cur[0]["rateBuy"]}/{cur[0]["rateSell"]}</code>'
    res += f'\n<b>EUR:</b> <code>{cur[1]["rateBuy"]}/{cur[1]["rateSell"]}</code>'
    res += f'\n<b>RUB:</b> <code>{cur[2]["rateBuy"]}/{cur[2]["rateSell"]}</code>'
    return res