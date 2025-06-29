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
import logging
import traceback

# Настройка базового логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),  # Вывод в консоль (Docker logs)
        logging.FileHandler('./logs/bot.log', encoding='utf-8'),  # Файл логов
    ]
)

logger = logging.getLogger(__name__)

load_dotenv()

# Токен бота
token = os.getenv("TOKEN")
if not token:
    logger.critical("TOKEN не найден в переменных окружения!")
    exit(1)

logger.info(f"🚀 Запуск бота ТехСтрим. Token: {token[:10]}...")

bot = telebot.TeleBot(token=token)

user_states = {}
button_states = {}
mistake = False

def check_email(email):
    """Проверка типа email для настройки SMTP"""
    logger.debug(f"Проверка email: {email}")
    
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
        logger.warning(f"Неподдерживаемый тип email: {email}")
        return None, None

def send_email(chat_id, email, password, message):
    """Отправка email через SMTP"""
    logger.info(f"📧 Отправка email для чата {chat_id}")
    
    try:
        email_type, port = check_email(email)
        if email_type:
            getter = email
            sender = email
            
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
            
            logger.info(f"✅ Email успешно отправлен для чата {chat_id}")
            bot.send_message(chat_id, "Сообщение успешно отправлено")
        else:
            logger.error(f"❌ Не удалось определить тип email: {email}")
            bot.send_message(chat_id, "Ошибка настройки email")
            
    except Exception as e:
        logger.error(f"❌ Ошибка в send_email: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        bot.send_message(chat_id, "Ошибка при отправке сообщения")

@bot.message_handler(commands=['start'])
def start(message):
    """Обработчик команды /start"""
    logger.info(f"👋 Команда /start от пользователя {message.from_user.first_name} (ID: {message.from_user.id})")
    
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('/start')
        item2 = types.KeyboardButton('Служба поддержки')
        item3 = types.KeyboardButton('Сообщить об ошибке')
        item4 = types.KeyboardButton('Справка')
        
        markup.add(item1, item2, item3, item4)
        button_states[message.from_user.id] = markup
        
        welcome_message = f"Добро пожаловать, {message.from_user.first_name}! Я корпоративный ассистент ТехСтрим AI, и я здесь, чтобы помочь с информацией о нашей компании."
        
        bot.send_message(message.from_user.id, welcome_message, reply_markup=markup)
        logger.info(f"✅ Приветствие отправлено пользователю {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в start_command: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        bot.send_message(message.from_user.id, "Произошла ошибка при запуске. Попробуйте позже.")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    """Основной обработчик текстовых сообщений"""
    global mistake
    chat_id = message.chat.id
    text = message.text
    user_name = message.from_user.first_name or "Неизвестный"
    
    logger.info(f"💬 Сообщение от {user_name} (ID: {chat_id}): {text}")
    
    try:
        markup = button_states.get(message.from_user.id, None)
        
        email = os.getenv("EMAIL")
        password = os.getenv("PASS")
        
        if not email or not password:
            logger.error("❌ EMAIL или PASS не настроены в переменных окружения")
            bot.send_message(chat_id, "Служба поддержки временно недоступна")
            return
        
        if markup:
            if text == 'Сообщить об ошибке':
                logger.info(f"🐛 Пользователь {chat_id} выбрал 'Сообщить об ошибке'")
                mistake = True
                bot.send_message(message.from_user.id, 
                    "Опишите найденную проблему или неточность одним сообщением", 
                    reply_markup=markup)
                    
            elif text == "Справка":
                logger.info(f"❓ Пользователь {chat_id} запросил справку")
                help_text = "Данный бот разработан для предоставления информации о IT-компании ТехСтрим, наших услугах, департаментах и сотрудниках. Вы можете задать любой вопрос о компании. В случае обнаружения ошибок или неточностей, используйте функции 'Служба поддержки' или 'Сообщить об ошибке'"
                bot.send_message(message.from_user.id, help_text, reply_markup=markup)
                
            elif text == 'Служба поддержки':
                logger.info(f"🆘 Пользователь {chat_id} обратился в службу поддержки")
                support_text = "Введите ваш запрос или обращение одним сообщением в формате /support ваше сообщение"
                bot.send_message(chat_id, support_text, reply_markup=markup)
                
            elif "/support" in text:
                logger.info(f"📞 Обработка запроса поддержки от {chat_id}")
                support_message = text.replace("/support ", "")
                send_email(chat_id=chat_id, email=email, password=password, message=support_message)
                
            else:
                if mistake:
                    logger.info(f"📝 Сохранение отчета об ошибке от {chat_id}")
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    try:
                        os.makedirs('./logs', exist_ok=True)  # Создаем директорию если нет
                        with open("./logs/error_reports.txt", "a", encoding='utf-8') as file:
                            file.write(f"\n{user_name} | {current_time} | {message.text}")
                        
                        bot.send_message(message.from_user.id, 
                            "Спасибо за обращение. Ваша информация будет обработана службой поддержки в ближайшее время", 
                            reply_markup=markup)
                        mistake = False
                        logger.info(f"✅ Отчет об ошибке сохранен от {chat_id}")
                        
                    except Exception as e:
                        logger.error(f"❌ Ошибка при сохранении отчета: {str(e)}")
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        bot.send_message(message.from_user.id, "Ошибка при сохранении отчета", reply_markup=markup)
                        
                else:
                    logger.info(f"🤖 Обработка запроса к AI от {chat_id}: {text}")
                    
                    try:
                        chatAI = AI()
                        logger.debug("✅ AI модуль инициализирован успешно")
                        
                        ai_response = chatAI.askAI(input_text=message.text)
                        logger.debug(f"📄 Получен ответ от AI: {ai_response[:100]}...")
                        
                        bot.send_message(message.from_user.id, ai_response, reply_markup=markup)
                        logger.info(f"✅ Ответ AI отправлен пользователю {chat_id}")
                        
                    except Exception as e:
                        logger.error(f"❌ Ошибка в AI_processing: {str(e)}")
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        error_message = "Извините, произошла ошибка при обработке вашего запроса. Попробуйте позже."
                        bot.send_message(message.from_user.id, error_message, reply_markup=markup)
        else:
            logger.warning(f"⚠️ Markup не найден для пользователя {chat_id}")
            bot.send_message(message.from_user.id, 
                "Произошла системная ошибка. Пожалуйста, начните заново с команды /start.")
                
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_text: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        bot.send_message(message.from_user.id, "Произошла неожиданная ошибка. Обратитесь в службу поддержки.")

if __name__ == "__main__":
    # Создаем директорию для логов
    os.makedirs('./logs', exist_ok=True)
    
    logger.info("🚀 Запуск polling для бота ТехСтрим...")
    
    try:
        bot.polling(none_stop=True, interval=0)
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.critical(f"🔥 Критическая ошибка бота: {str(e)}")
        logger.critical(f"Traceback: {traceback.format_exc()}")
