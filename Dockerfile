FROM python:3.8-slim
RUN pip install pika prometheus_client
COPY input.txt /app/input.txt
COPY . /app
WORKDIR /app