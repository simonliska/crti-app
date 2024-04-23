FROM python:3.8-slim
RUN pip install pika
COPY input.txt /app/input.txt
COPY . /app
WORKDIR /app