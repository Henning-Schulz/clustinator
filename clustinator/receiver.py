'''
@author: An Dang, Henning Schulz
'''

import pika
import argparse
import threading
import functools
from main import Main
from producer import Producer
from analysis.kneighbors import KNeighbors
from _warnings import warn
from pika.exceptions import StreamLostError, ChannelWrongStateError
from time import sleep


class Receiver:
    def __init__(self, rabbitmq_host, rabbitmq_port, timeout):
        print('Connecting to RabbitMQ at %r:%r...' % (rabbitmq_host, rabbitmq_port))
        
        while True:
        
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, heartbeat=timeout))
            channel = connection.channel()
            self.channel = channel
            
            clustering_queue = 'continuity.clustinator.task.clustinator.cluster'
            
            threads = []
            
            def clustering_work(method, body):
                Main(body, rabbitmq_host, rabbitmq_port).start()
                connection.add_callback_threadsafe(functools.partial(channel.basic_ack, method.delivery_tag))
            
            def clustering_callback(ch, method, properties, body):
                print(" [x] Received %r from %r" % (method.routing_key, clustering_queue))
                t = threading.Thread(target=clustering_work, args=(method, body))
                t.start()
                threads.append(t)
            
            self.__declare_exchange_and_queue(
                'continuity.task.clustinator.cluster',
                clustering_queue, clustering_callback)
            
            knn_queue = 'continuity.clustinator.task.clustinator.knndistance'
            
            def knn_distance_callback(ch, method, properties, body):
                print(' [x] Received %r from %r' % (method.routing_key, knn_queue))
                warn(('Need to do the work in the main thread. '
                      'Therefore, acked the message before processing it '
                      'and temporarily disconnected from RabbitMQ. '
                      'This will block all other activity.'))
                channel.basic_ack(delivery_tag=method.delivery_tag)
                connection.close()
                image = KNeighbors(body).distance_plot()
                Producer(method.routing_key, rabbitmq_host, rabbitmq_port).send_knn_image(image)
            
            self.__declare_exchange_and_queue(
                'continuity.task.clustinator.knndistance',
                knn_queue, knn_distance_callback)
            
            print('RabbitMQ connection established.', flush=True)
        
            try:
                channel.start_consuming()
            except (ChannelWrongStateError, StreamLostError):
                print('Reopening the RabbitMQ connection at %r:%r' % (rabbitmq_host, rabbitmq_port))
                continue
            except KeyboardInterrupt:
                channel.stop_consuming()
                break
            
        print('Shutting down...')
        
        for thread in threads:
            thread.join()
        
        print('Closing the RabbitMQ connection.')
        
        connection.close()
    
    def __declare_exchange_and_queue(self, exchange_name, queue_name, callback):
        self.channel.exchange_declare(exchange=exchange_name,
                                 exchange_type='topic', durable=False, auto_delete=True)

        self.channel.queue_declare(queue_name)
        self.channel.queue_bind(queue=queue_name, exchange=exchange_name, routing_key='#')

        self.channel.basic_consume(queue=queue_name, on_message_callback=callback)#, auto_ack=True)
        
        print('Listening to queue %r.' % queue_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start the clustinator listening to RabbitMQ.')
    parser.add_argument('--rabbitmq', nargs='?', default='localhost',
                   help='The host name or IP of the RabbitMQ server')
    parser.add_argument('--rabbitmq-port', nargs='?', type=int, default=pika.ConnectionParameters.DEFAULT_PORT,
                   help='The port number of the RabbitMQ server')
    parser.add_argument('--timeout', nargs='?', type=int, default=pika.ConnectionParameters.DEFAULT_HEARTBEAT_TIMEOUT,
                   help='The timeout in seconds after which the RabbitMQ connection is treated to be dead.')
    args = parser.parse_args()
    
    Receiver(args.rabbitmq, args.rabbitmq_port, args.timeout)
