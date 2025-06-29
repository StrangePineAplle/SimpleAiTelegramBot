from langchain_gigachat import GigaChat
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import warnings
import os
import logging
import traceback

warnings.filterwarnings('ignore')

# Получаем существующий логгер
logger = logging.getLogger(__name__)

class AI:
    def __init__(self, pathToData="./data/company_data.txt", key=None):
        logger.info("🤖 Инициализация AI модуля ТехСтрим")
        
        if key is None: 
            key = "ZDVkODE5NjctMTJiZS00ZmE1LWI1ZGItNGRiYjg4OWJkMjQ1OjdlMjMwZjUyLWRlMzItNGE4NS05YzcwLWYyMDBiZjk5N2IwZg=="
            logger.debug("🔑 Используется ключ GigaChat по умолчанию")
        
        self.pathToData = pathToData
        
        try:
            # Проверяем файл данных
            if not os.path.exists(pathToData):
                logger.warning(f"⚠️ Файл данных не найден: {pathToData}")
                self.documents = [{"page_content": "ТехСтрим - инновационная IT-компания, основанная в 2018 году в Санкт-Петербурге."}]
            else:
                logger.info(f"📁 Загрузка данных из файла: {pathToData}")
                with open(pathToData, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                if not content.strip():
                    logger.warning("⚠️ Файл данных пуст")
                    content = "ТехСтрим - инновационная IT-компания."
                
                self.documents = [{"page_content": content}]
                logger.info(f"✅ Данные загружены успешно. Размер: {len(content)} символов")
            
            # Инициализация GigaChat
            logger.info("🔄 Инициализация GigaChat...")
            giga = GigaChat(
                credentials=key,
                model='GigaChat:latest',
                verify_ssl_certs=False
            )
            logger.info("✅ GigaChat инициализирован успешно")
            
            prompt = PromptTemplate(
                input_variables=["input_documents", "question"],
                template="""
            Ты корпоративный ИИ-ассистент IT-компании ТехСтрим - инновационной технологической компании, основанной в 2018 году.

            ПРАВИЛА РАБОТЫ:
            1. ИДЕНТИФИКАЦИЯ: На вопросы "кто ты?" отвечай: "Я корпоративный ассистент ТехСтрим AI"
            2. ОБЛАСТЬ КОМПЕТЕНЦИИ: Отвечай только на вопросы о ТехСтрим - услуги, сотрудники, контакты, департаменты, проекты
            3. ОТКАЗ: При вопросах вне тематики компании отвечай: "Я специализируюсь только на вопросах о деятельности ТехСтрим. Задайте вопрос о нашей компании, услугах или сотрудниках."

            СТИЛЬ ОТВЕТОВ:
            - Профессиональный и дружелюбный тон
            - Конкретная полезная информация
            - Структурированная подача данных
            - Указание контактов при релевантности
            - По возможности будь краток, давай тольео ту информацию о которой тебя просили
            - Не используй форматирование
            База знаний о ТехСтрим:
            {context}

            Вопрос: {question}

            Мой ответ как ассистент ТехСтрим:
            """
            )
            
            self.chain = LLMChain(prompt=prompt, llm=giga)
            logger.info("✅ AI цепочка создана успешно")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации AI: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def askAI(self, input_text='Расскажи о компании ТехСтрим'):
        logger.info(f"🔍 Обработка запроса: {input_text[:50]}...")
        
        try:
            # Подготавливаем документы для передачи
            docs_text = ""
            for doc in self.documents:
                if hasattr(doc, 'page_content'):
                    docs_text += doc.page_content + "\n"
                elif isinstance(doc, dict) and 'page_content' in doc:
                    docs_text += doc['page_content'] + "\n"
                else:
                    docs_text += str(doc) + "\n"
            
            logger.debug(f"📊 Размер контекста: {len(docs_text)} символов")
            
            # Отправляем запрос к AI
            logger.debug("🚀 Отправка запроса к GigaChat...")
            result = self.chain.invoke({
                "input_documents": docs_text,
                "question": input_text
            })
            
            response = result["text"]
            logger.info(f"✅ Получен ответ от AI: {len(response)} символов")
            logger.debug(f"📝 Ответ: {response[:200]}...")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Ошибка в askAI: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return "Извините, произошла ошибка при обработке вашего запроса. Попробуйте позже."
