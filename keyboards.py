from aiogram.types import ReplyKeyboardMarkup
keyboard = ReplyKeyboardMarkup(True)
keyboard.row('Баланс')
keyboard.row('Курс валют')
keyboard.row('Настройки')

keyboardOpt = ReplyKeyboardMarkup(True)
keyboardOpt.row('Управление токеном')
keyboardOpt.row('Переключить режим откладки')
keyboardOpt.row('Сбросить настройки')
keyboardOpt.row('Назад')

keyboardToken = ReplyKeyboardMarkup(True)
keyboardToken.row('Просмотреть токен')
keyboardToken.row('Изменить токен')
keyboardToken.row('Удалить токен')
keyboardToken.row('Назад')

keyboardDelToken = ReplyKeyboardMarkup(True)
keyboardDelToken.row('Да', 'Нет')

keyboardBack = ReplyKeyboardMarkup(True)
keyboardBack.row('Назад')