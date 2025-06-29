FROM python:3.9-slim

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /TGBOT

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Обновляем pip до последней версии
RUN pip install --no-cache-dir --upgrade pip

# Копируем и устанавливаем зависимости по одной для лучшего кэширования
COPY requirements.txt .

# Устанавливаем зависимости с подробным выводом
RUN pip install --no-cache-dir -v -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем необходимые директории
RUN mkdir -p /TGBOT/data /TGBOT/logs

# Проверяем, что модули установлены
RUN python -c "import langchain_community; print('langchain_community OK')"
RUN python -c "from langchain_community.document_loaders import TextLoader; print('TextLoader OK')"

CMD ["python", "./Telegram.py"]
