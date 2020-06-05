FROM python:3.8-slim

USER root
RUN apt update && apt install -y -qq ffmpeg

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "280", "hello:app"]