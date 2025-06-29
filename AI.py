from langchain_gigachat import GigaChat
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import warnings
import os

warnings.filterwarnings('ignore')

class AI:
    def __init__(self, pathToData="./data/company_data.txt", key=None):
        if key is None: 
            key = "ZDVkODE5NjctMTJiZS00ZmE1LWI1ZGItNGRiYjg4OWJkMjQ1OjdlMjMwZjUyLWRlMzItNGE4NS05YzcwLWYyMDBiZjk5N2IwZg=="
        
        self.pathToData = pathToData
        
        # Загружаем данные простым способом
        try:
            with open(pathToData, 'r', encoding='utf-8') as file:
                content = file.read()
            self.documents = content
        except FileNotFoundError:
            print(f"Файл {pathToData} не найден, используем базовые данные")
            self.documents = "ТехСтрим - инновационная IT-компания, основанная в 2018 году."
        
        # GigaChat
        giga = GigaChat(
            credentials=key,
            model='GigaChat:latest',
            verify_ssl_certs=False
        )
        
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

        База знаний о ТехСтрим:
        {input_documents}

        Вопрос: {question}

        Мой ответ как ассистент ТехСтрим:
        """
        )

        
        self.chain = LLMChain(prompt=prompt, llm=giga)
    
    def askAI(self, input_text='Расскажи о компании ТехСтрим'):
        try:
            result = self.chain.invoke({
                "context": self.documents,
                "question": input_text
            })
            return result["text"]
        except Exception as e:
            print(f"Ошибка: {e}")
            return "Извините, произошла ошибка при обработке запроса."
