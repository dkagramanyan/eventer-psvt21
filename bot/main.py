from config import token, pin, database as db
import telebot
from telebot import types
import psycopg2 as psy
from psycopg2 import OperationalError

bot = telebot.TeleBot(token)
logged_users = {}


def connect_to_database():
    try:
        conn = psy.connect(user=db['user'],
                           password=db['password'],
                           host=db['host'],
                           port=db['port'],
                           database=db['database'])
        return conn
    except OperationalError as error:
        print('Ошибка при работе с PostgreSQL', error)


connection = connect_to_database()


def name(message):
    first_name = bot.send_message(message.chat.id, 'Напиши свое имя')
    bot.register_next_step_handler(first_name, save_first_name)


def save_first_name(message):
    first_name = message.text
    last_name = bot.send_message(message.chat.id, 'Напиши свою фамилию')
    bot.register_next_step_handler(last_name, save_last_name, first_name)


def save_last_name(message, first_name):
    last_name = message.text
    if first_name != 'Фамилии' and last_name != '':
        give_schedule_by_name_and_surname(message, first_name, last_name)
    elif first_name == 'Фамилии' and last_name != '':
        give_schedule_by_surname(message, last_name)


def give_schedule_by_name_and_surname(message, first_name, last_name):
    global connection
    cursor = connection.cursor()

    cursor.execute("SELECT id "
                   "FROM plat_people_main "
                   "WHERE similarity(first_name, %s) > 0.5 AND similarity(middle_name, %s) > 0.5",
                   (first_name, last_name))
    person_id = cursor.fetchone()[0]

    cursor.execute("SELECT name, time_from, time_to "
                   "FROM plat_people_main as ppm "
                   "JOIN plat_timetable_main as ptm ON ppm.id = ptm.org_id "
                   "JOIN plat_timetable_cases as ptc ON ptm.event_id = ptc.id "
                   "WHERE org_id = %s", (person_id, ))
    schedule = cursor.fetchall()

    bot.send_message(message.chat.id, f'Название: {schedule[0][0]}\n'
                                      f'Время начала: {str(schedule[0][1])[:2]}:{str(schedule[0][1])[2:]}\n'
                                      f'Время конца: {str(schedule[0][2])[:2]}:{str(schedule[0][2])[2:]}')


def give_schedule_by_surname(message, last_name):
    global connection
    cursor = connection.cursor()

    cursor.execute("SELECT id "
                   "FROM plat_people_main "
                   "WHERE similarity(middle_name, %s) > 0.5",
                   (last_name, ))
    person_id = cursor.fetchone()[0]

    cursor.execute("SELECT name, time_from, time_to "
                   "FROM plat_people_main as ppm "
                   "JOIN plat_timetable_main as ptm ON ppm.id = ptm.org_id "
                   "JOIN plat_timetable_cases as ptc ON ptm.event_id = ptc.id "
                   "WHERE org_id = %s", (person_id, ))
    schedule = cursor.fetchall()

    bot.send_message(message.chat.id, f'Название: {schedule[0][0]}\n'
                                      f'Время начала: {str(schedule[0][1])[:2]}:{str(schedule[0][1])[2:]}\n'
                                      f'Время конца: {str(schedule[0][2])[:2]}:{str(schedule[0][2])[2:]}')


@bot.message_handler(commands=['start'])
def hello_message(message):
    bot.send_message(message.chat.id, 'Привет!\nЯ рад видеть тебя на этом прекрасном мероприятии')
    pin_code = bot.send_message(message.chat.id, 'Введите пароль!')
    bot.register_next_step_handler(pin_code, try_pin)


def try_pin(message):
    if message.text.lower() == pin:
        bot.send_message(message.chat.id, 'Введен правильный пароль. Доступ открыт!')
        logged_users[message.chat.first_name] = message.chat.id
        bot.send_message(message.chat.id, 'Нажмите /help, чтобы узнать о командах')
    else:
        bot.send_message(message.chat.id, 'Неверный пароль, попробуйте еще раз!')


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id,
                     f'В нашем боте существуют такие команды:\n'
                     f'/start — полностью начинает работу бота заново\n'
                     f'/help — выводит команды, которые существуют в боте\n'
                     f'/schedule - выводит ваше расписание'
                     )


@bot.message_handler(commands=['schedule'])
def give_schedule(message):
    buttons = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    surname = types.KeyboardButton('Фамилии')
    name_and_surname = types.KeyboardButton('Фамилии и имени')

    buttons.add(surname, name_and_surname)

    bot.send_message(message.chat.id, 'По этой команде вы можете получить свое расписание!\nПоиск по:',
                     reply_markup=buttons)


@bot.message_handler(content_types=['text'])
def handler(message):
    if message.text == 'Фамилии':
        save_first_name(message)
    elif message.text == 'Фамилии и имени':
        name(message)


bot.polling()
