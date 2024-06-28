FROM ubuntu:22.04

WORKDIR /TGBOT

COPY . /TGBOT/

RUN apt-get update && apt-get install -y python3 pip

RUN pip install -r requirements.txt

CMD [ "python3", "./Telegram.py" ]