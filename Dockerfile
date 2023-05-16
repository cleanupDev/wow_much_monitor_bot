FROM python:3.9-slim-bullseye

ENV ADDRESS=default
ENV API_KEY=default
ENV TELEGRAM_TOKEN=default
ENV CHAT_ID=default
ENV BOT_NAME=default
ENV METHOD_ID=default

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "wow_such_monitor.py"]

