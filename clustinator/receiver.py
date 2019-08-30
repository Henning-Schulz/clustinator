'''
@author: An Dang, Henning Schulz
'''

import pika
import argparse
from main import Main


class Receiver:
    def __init__(self, rabbitmq_host, rabbitmq_port):
        print('Connecting to RabbitMQ at %r:%r...' % (rabbitmq_host, rabbitmq_port))
        
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port))
        channel = connection.channel()
        channel.exchange_declare(exchange='continuity.task.clustinator.cluster',
                                 exchange_type='topic', durable=False, auto_delete=True)

        result = channel.queue_declare("continuity.clustinator.task.clustinator.cluster")
        queue_name = result.method.queue
        channel.queue_bind(queue=queue_name,
                           exchange='continuity.task.clustinator.cluster', routing_key='#')

        def callback(ch, method, properties, body):
            print(" [x] Received %r from %r" % (method.routing_key, queue_name))#, body))
            Main(body).start()

        channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True)
        
        print('Listening to queue %r.' % queue_name, flush=True)
        
        channel.start_consuming()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start the clustinator listening to RabbitMQ.')
    parser.add_argument('--rabbitmq', nargs='?', default='localhost',
                   help='The host name or IP of the RabbitMQ server')
    parser.add_argument('--rabbitmq-port', nargs='?', type=int, default=pika.ConnectionParameters.DEFAULT_PORT,
                   help='The port number of the RabbitMQ server')
    args = parser.parse_args()
    
    Receiver(args.rabbitmq, args.rabbitmq_port)
