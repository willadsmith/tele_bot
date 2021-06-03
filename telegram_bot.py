import telebot
from telebot import types

TOKEN = '1741375451:AAF7PU55BI5PYuSFMUsLUbrPRuU2QvGS00I'

bot = telebot.TeleBot(TOKEN)

users = [
    {
        'name': 'admin',
        'pass': 'qwerty'
    }
]

action = None
login_auth = None
pass_auth = None
login_sign = None
pass_sign = None
choose_user = ''

cur_user = {
    'name': login_auth,
    'pass': pass_auth
}


def clean_state():
    global action, login_auth, pass_auth, login_sign, pass_sign
    action = None
    login_auth = None
    pass_auth = None
    login_sign = None
    pass_sign = None


@bot.message_handler(commands=['start'])
def start(msg):
    markup = types.InlineKeyboardMarkup()
    if login_auth is None:
        markup.add(types.InlineKeyboardButton(text='Войти', callback_data='login'))
        markup.add(types.InlineKeyboardButton(text='Зарегистрироваться', callback_data='sign'))
    if login_auth == 'admin':
        markup.add(types.InlineKeyboardButton(text='Отобразить список пользователей', callback_data='list_users'))
    if login_auth == 'admin':
        markup.add(types.InlineKeyboardButton(text='Удалить пользователя', callback_data='del_user'))
    if login_auth is not None:
        markup.add(types.InlineKeyboardButton(text='Выйти', callback_data='back'))

    bot.send_message(msg.chat.id, 'Выберите действие', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query_func(call):
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.delete_message(call.message.chat.id, call.message.id - 1)
    global action, login_auth, login_sign, pass_auth, pass_sign, users, choose_user
    if call.data == 'login':
        action = 'login'
        bot.send_message(call.message.chat.id, 'Введите логин')
    if call.data == 'sign':
        action = 'sign'
        bot.send_message(call.message.chat.id, 'Введите предпочитаемый логин')
    if call.data == 'del_user':
        bot.send_message(call.message.chat.id, 'Укажите логин пользователя, который необходимо удалить')
        for user in users:
            markup = types.InlineKeyboardMarkup()
            choose_user += user['name'] + '\n'
            markup.add(types.InlineKeyboardButton(text=f'{choose_user}', callback_data=f'{choose_user}'))
    if call.data == 'list_users':
        list_user = ''
        for user in users:
            list_user += user['name'] + '\n'
        bot.send_message(call.message.chat.id, list_user)
    if call.data == 'back':
        clean_state()
        bot.send_message(call.message.chat.id,
                         'Вы успешно вышли! Для авторизации или регистрации воспользуйтесь /start')


def login_act(value):
    global action, login_auth, pass_auth
    for x in range(len(users)):
        if users[x]['name'] == value.text:
            login_auth = users[x]['name']
            cur_user['name'] = value.text
            bot.send_message(value.chat.id, 'Введите пароль')
            return
    bot.send_message(value.chat.id, 'Пользователь не найден, повторите через команду /start')


def pass_act(value):
    global action, login_auth, pass_auth
    for user in users:
        if cur_user['name'] == user['name'] and user['pass'] == value.text:
            bot.send_message(value.chat.id, 'Вы успешно авторизованы! Для продолжения введите /start')
            pass_auth = value.text
            return
    bot.send_message(value.chat.id, 'Неверный пароль')


def sign_act(value):
    global login_sign, pass_sign
    for user in users:
        if user['name'] == value.text:
            bot.send_message(value.chat.id, 'Данный логин уже зарегистрирован')
            return
    login_sign = value.text
    bot.send_message(value.chat.id, 'Введите предпочитаемый пароль')


def sign_pass(value):
    global action, login_sign, pass_sign
    if value.text == '':
        bot.send_message(value.chat.id, 'Необходимо ввести пароль!')
        return
    pass_sign = value.text
    users.append({'name': login_sign, 'pass': pass_sign})
    bot.send_message(value.chat.id, 'Пользователь успешно создан! Войдите командой /start')
    clean_state()


@bot.message_handler(content_types=['text'])
def text(msg):
    global action, login_auth, pass_auth, login_sign, pass_sign, choose_user

    if action == 'login' and login_auth is None:
        login_act(msg)
    elif action == 'login' and pass_auth is None:
        pass_act(msg)
    elif login_auth is not None and pass_sign is not None:
        action = None
    elif action == 'sign' and login_sign is None:
        sign_act(msg)
    elif action == 'sign' and pass_sign is None:
        sign_pass(msg)
    elif action == 'del_user':
        bot.send_message(msg.chat.id, f'Удалить пользователя {choose_user}?')
    else:
        action = None
        bot.send_message(msg.chat.id, 'Ошибка выбора действий, воспользуйтесь командой /start')
        return


bot.polling()
