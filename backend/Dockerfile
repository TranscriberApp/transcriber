FROM python:3.8-slim

USER root
COPY . /app/backend

WORKDIR /app/backend

RUN apt update && apt install -y -qq ffmpeg

RUN pip install -r requirements.txt

WORKDIR /app

EXPOSE 8000
CMD ["python", "-m", "backend.app"]