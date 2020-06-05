FROM python:3.8-slim

RUN apt update && apt install -y -qq ffmpeg

RUN pip install -r requirements.txt

RUN ["gunicorn", "--timeout", "280", "hello:app"]