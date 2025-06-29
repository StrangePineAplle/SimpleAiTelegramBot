import telebot
from telebot import types
import os
from AI import AI
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота, который вы получили от BotFather
token = os.getenv("TOKEN")
bot = telebot.TeleBot(token=token)

user_states = {}
# Словарь для хранения состояния кнопок
button_states = {}
mistake = False

def check_email(email):
    port = 0
    if "@gmail.com" in email:
        port = 587
        return "smtp.gmail.com", port
    elif "@mail.ru" in email:
        port = 25
        return "smtp.mail.ru", port
    elif "@yandex.ru" in email:
        port = 465
        return "smtp.yandex.ru", port
    elif "@zoho.com" in email:
        port = 587
        return "smtp.zoho.com", port
    else:
        return None, None

def send_email(chat_id, email, password, message):
    email_type, port = check_email(email)
    if email_type:
        getter = email
        sender = email
        password = password
        
        msg = MIMEMultipart()
        subject = "Запрос из корпоративного бота ТехСтрим"
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = sender
        msg['To'] = getter
        
        msg.attach(MIMEText(message, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(email_type, port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender, password)
        server.sendmail(sender, getter, msg.as_string())
        server.quit()
        
        bot.send_message(chat_id, "Сообщение успешно отправлено")

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('/start')
    item2 = types.KeyboardButton('Служба поддержки')
    item3 = types.KeyboardButton('Сообщить об ошибке')
    item4 = types.KeyboardButton('Справка')
    
    markup.add(item1, item2, item3, item4)
    button_states[message.from_user.id] = markup
    
    bot.send_message(message.from_user.id, 
        "Добро пожаловать, {0.first_name}! Я корпоративный ассистент ТехСтрим AI, и я здесь, чтобы помочь с информацией о нашей компании.".format(message.from_user), 
        reply_markup=markup)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    global mistake
    chat_id = message.chat.id
    markup = button_states.get(message.from_user.id, None)
    text = message.text
    
    email = os.getenv("EMAIL")
    password = os.getenv("PASS")
    
    if markup:
        if text == 'Сообщить об ошибке':
            mistake = True
            bot.send_message(message.from_user.id, 
                "Опишите найденную проблему или неточность одним сообщением", 
                reply_markup=markup)
        elif text == "Справка":
            bot.send_message(message.from_user.id, 
                "Данный бот разработан для предоставления информации о IT-компании ТехСтрим, наших услугах, департаментах и сотрудниках. Вы можете задать любой вопрос о компании. В случае обнаружения ошибок или неточностей, используйте функции 'Служба поддержки' или 'Сообщить об ошибке'", 
                reply_markup=markup)
        elif text == 'Служба поддержки':
            bot.send_message(chat_id, 
                "Введите ваш запрос или обращение одним сообщением в формате /support ваше сообщение", 
                reply_markup=markup)
        elif "/support" in text:
            text = text.replace("/support ", "")
            send_email(chat_id=chat_id, email=email, password=password, message=text)
        else:
            if mistake:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open("./logs/error_reports.txt", "a") as file:
                    file.write(f"\n{message.from_user.first_name} | {current_time} | {message.text}")
                bot.send_message(message.from_user.id, 
                    "Спасибо за обращение. Ваша информация будет обработана службой поддержки в ближайшее время", 
                    reply_markup=markup)
                mistake = False
            else:
                chatAI = AI()
                bot.send_message(message.from_user.id, 
                    chatAI.askAI(input=message.text), 
                    reply_markup=markup)
    else:
        bot.send_message(message.from_user.id, 
            "Произошла системная ошибка. Пожалуйста, начните заново с команды /start.")

bot.polling(none_stop=True, interval=0)
