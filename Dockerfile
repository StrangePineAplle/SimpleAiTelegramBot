FROM python:3.9-slim

WORKDIR /TGBOT

# Сначала копируем только requirements для кэширования pip install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Потом копируем остальные файлы
COPY Telegram.py AI.py ./
COPY data/ ./data/
RUN mkdir -p logs

CMD ["python", "Telegram.py"]
