from langchain import LLMChain
from langchain.prompts import PromptTemplate
from langchain_gigachat import GigaChat
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import warnings
import os

warnings.filterwarnings('ignore')

class AI:
    def __init__(self, pathToData="./data/company_data.txt", key=None):
        if key is None: 
            key = "ZDVkODE5NjctMTJiZS00ZmE1LWI1ZGItNGRiYjg4OWJkMjQ1OjdlMjMwZjUyLWRlMzItNGE4NS05YzcwLWYyMDBiZjk5N2IwZg=="
        
        self.pathToData = pathToData
        
        # Проверяем существование файла
        if not os.path.exists(pathToData):
            print(f"Предупреждение: файл {pathToData} не найден!")
            # Создаем минимальные данные
            self.documents = [{"page_content": "ТехСтрим - инновационная IT-компания, основанная в 2018 году в Санкт-Петербурге."}]
        else:
            # Загружаем корпоративные данные ТехСтрим
            loader = TextLoader(self.pathToData, encoding='UTF-8')
            documents = loader.load()
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=0,
                length_function=len,
                is_separator_regex=False,
            )
            
            self.documents = text_splitter.split_documents(documents)
        
        # Инициализация GigaChat
        giga = GigaChat(
            credentials=key,
            model='GigaChat:latest',
            verify_ssl_certs=False
        )
        
        # Создаем промпт без использования hub
        prompt = PromptTemplate(
            input_variables=["input_documents", "question"],
            template="""
Ты корпоративный ассистент IT-компании ТехСтрим. 
Используй предоставленную информацию о компании для ответа на вопросы.

Информация о компании:
{input_documents}

Вопрос пользователя: {question}

Дай подробный и полезный ответ на основе информации о ТехСтрим:
"""
        )
        
        self.chain = LLMChain(prompt=prompt, llm=giga)
    
    def askAI(self, input_text='Расскажи о компании ТехСтрим'):
        try:
            # Подготавливаем документы для передачи
            docs_text = ""
            for doc in self.documents:
                if hasattr(doc, 'page_content'):
                    docs_text += doc.page_content + "\n"
                else:
                    docs_text += str(doc) + "\n"
            
            result = self.chain.invoke({
                "input_documents": docs_text,
                "question": input_text
            })
            
            return result["text"]
        except Exception as e:
            print(f"Ошибка в askAI: {e}")
            return "Извините, произошла ошибка при обработке вашего запроса. Попробуйте позже."
