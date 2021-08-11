#Скрипт для запроса курса валют через api монобанка раз в пол часа
from requests import get
from time import sleep

#Бесконечный луп
while True:
    #Запрос курсов
    req = get("https://api.monobank.ua/bank/currency").text
    if "errorDescription" not in req:
    #Сохранение запроса
        cur = open("currency.json", "w")
        cur.write(req)
        cur.close()
        print('Done')
    else:
    #Вывод ошибки при ошибке
        print('Error')
    #Задержка 30 минут
    sleep(1800)