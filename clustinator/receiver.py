import pika
from main import Main


class Receiver:
    def __init__(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange='continuity.task.clustinator.cluster',
                                 exchange_type='topic', durable=False, auto_delete=True)

        result = channel.queue_declare("continuity.clustinator.task.clustinator.cluster")
        queue_name = result.method.queue
        channel.queue_bind(queue=queue_name,
                           exchange='continuity.task.clustinator.cluster', routing_key='#')

        def callback(ch, method, properties, body):
            print(" [x] %r%r" % (method.routing_key, body))
            Main(body).start()

        channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True)
        channel.start_consuming()


if __name__ == '__main__':
    Receiver()
