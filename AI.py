from langchain_community.chat_models.gigachat import GigaChat
from langchain import hub
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import LLMChain
import warnings
import httpx
warnings.filterwarnings('ignore')

client = httpx.Client(timeout=httpx.Timeout(10.0))

class AI:
    def __init__(self, pathToData = "./data/data_x.txt", key = None):
        if key == None: key = "ZjdiZmQzZDktNWRmMC00MGZhLTk4ZTItNDMzNTk4YTNkODcxOjlmYjYzNTQwLTZiNTMtNGUyNy1iZTY2LTUyYzI3YmNlNjE1MQ=="
        self.pathToData = pathToData

        auth = key #ключь доступа
        giga = GigaChat(credentials=auth,
                        model='GigaChat:latest',
                        verify_ssl_certs=False
                        )

        loader = TextLoader(self.pathToData, encoding = 'UTF-8') # загружаем файл для пересказа
        self.documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter( # дробим на чанки
            chunk_size = 1000,
            chunk_overlap  = 0,
            length_function = len,
            is_separator_regex = False,
        )

        self.documents = text_splitter.split_documents(self.documents)
        bonch_promt =  hub.pull("moneco/bonch_promt")
        self.chain = LLMChain(prompt=bonch_promt, llm=giga)


    def askAI(self,chain = None, documents = None, input = 'Кто ты?'):
        if chain == None: chain = self.chain
        if documents == None: documents = self.documents

        res = chain.invoke({ # обращаемся к нейронке
        "input_documents": documents,
        "question" : input
        })
        return res["text"]
