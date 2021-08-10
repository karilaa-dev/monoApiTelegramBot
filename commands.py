import time
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

def tCurrent():
    return int(time.time())

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
