'''
@author: An Dang, Henning Schulz
'''

import pika


class Producer:
    def __init__(self, app_id, rabbitmq_host, rabbitmq_port):
        self.app_id = app_id
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_port = rabbitmq_port
    
    def __send_message(self, message, exchange_name, content_type = None):
        print('Sending results to RabbitMQ at %r:%r...' % (self.rabbitmq_host, self.rabbitmq_port))
        
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbitmq_host, port=self.rabbitmq_port))
        channel = connection.channel()

        channel.exchange_declare(exchange=exchange_name,
                                 exchange_type='topic', durable=False, auto_delete=True)

        if content_type != None:
            content_type_props = pika.spec.BasicProperties(content_type=content_type)
        else:
            content_type_props = None
        
        channel.basic_publish(
                exchange=exchange_name, routing_key=self.app_id, body=message,
                properties=content_type_props)

        print(" [x] Sent to %r to %r" % (self.app_id, exchange_name))

        connection.close()
    
    def send_clustering(self, message):
        self.__send_message(message, 'continuity.event.clustinator.finished', content_type='application/json')
    
    def send_knn_image(self, image):
        self.__send_message(image, 'continuity.event.clustinator.imagegenerated')
