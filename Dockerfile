FROM python:3.6.7

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY clustinator ./

ENTRYPOINT echo "Waiting a bit for RabbitMQ..."; sleep 7; python ./receiver.py --rabbitmq=${RABBITMQ:-rabbitmq}