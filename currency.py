from requests import get
from time import sleep
import datetime

#Текущее время
def timenow():
    return datetime.datetime.today().strftime("%B %d %H:%M:%S")

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