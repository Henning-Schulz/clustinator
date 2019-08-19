import pika
import sys


class Producer:
    def __init__(self, message, app_id):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.exchange_declare(exchange='continuity.event.clustinator.finished',
                                 exchange_type='topic', durable=False, auto_delete=True)
        routing_key = app_id

        content_type = pika.spec.BasicProperties(content_type='application/json')
        channel.basic_publish(
            exchange='continuity.event.clustinator.finished', routing_key=routing_key, body=message,
            properties=content_type)

        print(" [x] Sent %r:%r" % (routing_key, message))

        connection.close()
