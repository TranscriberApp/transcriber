FROM python:3.8-slim

USER root
COPY . /app/backend

WORKDIR /app/backend

RUN apt update && apt install -y -qq ffmpeg

RUN pip install -r requirements.txt

WORKDIR /app

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "280", "app:app"]