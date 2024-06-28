.PHONY:

run:
	python3 Telegram.py

image: 
	sudo docker build . -t bai

docker: 
	sudo docker run --name=tgbot -d bai