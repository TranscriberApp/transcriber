FROM python:3.8-slim

USER root
RUN apt update && apt install -y -qq ffmpeg

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

RUN ["gunicorn", "--timeout", "280", "hello:app"]