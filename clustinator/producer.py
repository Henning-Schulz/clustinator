'''
@author: An Dang, Henning Schulz
'''

import pika


class Producer:
    def __init__(self, message, app_id, rabbitmq_host, rabbitmq_port):
        print('Sending results to RabbitMQ at %r:%r...' % (rabbitmq_host, rabbitmq_port))
        
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port))
        channel = connection.channel()
        
        exchange_name = 'continuity.event.clustinator.finished'

        channel.exchange_declare(exchange=exchange_name,
                                 exchange_type='topic', durable=False, auto_delete=True)
        routing_key = app_id

        content_type = pika.spec.BasicProperties(content_type='application/json')
        channel.basic_publish(
            exchange=exchange_name, routing_key=routing_key, body=message,
            properties=content_type)

        print(" [x] Sent to %r to %r" % (routing_key, exchange_name))

        connection.close()
