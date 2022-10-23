FROM python:3.10.8-alpine

RUN mkdir /app

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

WORKDIR /app/bot

ENTRYPOINT [ "python",  "bot.py" ]

