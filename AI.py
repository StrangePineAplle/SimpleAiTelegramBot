# Исправленные импорты для GigaChat
try:
    # Пробуем новый путь (langchain-gigachat)
    from langchain_gigachat import GigaChat
except ImportError:
    try:
        # Fallback на старый путь (langchain-community)
        from langchain_community.chat_models.gigachat import GigaChat
    except ImportError:
        # Альтернативный импорт
        from langchain_community.chat_models import GigaChat

from langchain import hub
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import LLMChain
import warnings
import httpx

warnings.filterwarnings('ignore')
client = httpx.Client(timeout=httpx.Timeout(10.0))

class AI:
    def __init__(self, pathToData = "./data/company_data.txt", key = None):
        if key == None: 
            key = "ZDVkODE5NjctMTJiZS00ZmE1LWI1ZGItNGRiYjg4OWJkMjQ1OjdlMjMwZjUyLWRlMzItNGE4NS05YzcwLWYyMDBiZjk5N2IwZg=="
        
        self.pathToData = pathToData
        auth = key  # ключ доступа к GigaChat
        
        giga = GigaChat(credentials=auth,
                       model='GigaChat:latest',
                       verify_ssl_certs=False)
        
        # Загружаем корпоративные данные ТехСтрим
        loader = TextLoader(self.pathToData, encoding = 'UTF-8')
        self.documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 0,
            length_function = len,
            is_separator_regex = False,
        )
        
        self.documents = text_splitter.split_documents(self.documents)
        
        # Создаем простой промпт, если hub недоступен
        try:
            techstream_prompt = hub.pull("moneco/techstream_corporate_assistant")
        except:
            from langchain.prompts import PromptTemplate
            techstream_prompt = PromptTemplate(
                input_variables=["input_documents", "question"],
                template="""
                Используя предоставленную информацию о компании ТехСтрим, ответь на вопрос пользователя.
                
                Информация о компании:
                {input_documents}
                
                Вопрос: {question}
                
                Ответ:
                """
            )
        
        self.chain = LLMChain(prompt=techstream_prompt, llm=giga)
    
    def askAI(self, chain = None, documents = None, input = 'Расскажи о компании ТехСтрим'):
        if chain == None: chain = self.chain
        if documents == None: documents = self.documents
        
        res = chain.invoke({
            "input_documents": documents,
            "question" : input
        })
        
        return res["text"]
