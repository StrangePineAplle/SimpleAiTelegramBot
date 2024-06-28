
import telebot
from telebot import types
from datetime import datetime
from AI import AI


bot = telebot.TeleBot('7185617704:AAHgY9piyPqsw4V9bjRSl-CsOJ3WcpR9SUg')

# Словарь для хранения состояния кнопок
button_states = {}
mistake = False

@bot.message_handler(commands=['start'])
def start(message):
    # Создание кнопок
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('/start')
    item2 = types.KeyboardButton('Разрабочики')
    item3 = types.KeyboardButton('Нашел Ошибку')
    markup.add(item1, item2, item3)

    # Сохранение состояния кнопок в словаре
    button_states[message.from_user.id] = markup

    bot.send_message(message.from_user.id, "Привет, {0.first_name}! Я телеграм бот BAI, и я здесь, чтобы сделать вашу студенческую жизнь проще.".format(message.from_user), reply_markup=markup)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    global mistake
    # Получение состояния кнопок из словаря
    markup = button_states.get(message.from_user.id, None)

    if markup:
        if message.text == 'Нашел Ошибку':
            mistake = True
            bot.send_message(message.from_user.id, "Напишите найденную неточность 1 сообщением :", reply_markup=markup)
        elif message.text == 'Разрабочики':
            bot.send_message(message.from_user.id, "Для связи c создателями пишите на :BaiHelp@mail.ru", reply_markup=markup)
        else:
            if mistake:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open("./logs/errorList.txt", "a") as file:
                    file.write(f"\n{message.from_user.first_name} | {current_time} | {message.text}")
                bot.send_message(message.from_user.id, "Ваша информация будет обработана в ближайшее время ",reply_markup=markup)
                mistake = False
            else:
                chatAI = AI()
                bot.send_message(message.from_user.id, chatAI.askAI(input=message.text) , reply_markup=markup)
    else:
        bot.send_message(message.from_user.id, "Произошла ошибка. Пожалуйста, начните заново с команды /start.")

bot.polling(none_stop=True, interval=0)
