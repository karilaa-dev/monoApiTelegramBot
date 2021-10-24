from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
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

reset_accept = InlineKeyboardButton('Да', callback_data='reset_accept')
reset_cancel = InlineKeyboardButton('Нет', callback_data='reset_cancel')
reset_buttons = InlineKeyboardMarkup().add(reset_accept, reset_cancel)

add_token = InlineKeyboardMarkup().add(InlineKeyboardButton('Добавить токен', callback_data='add_token'))