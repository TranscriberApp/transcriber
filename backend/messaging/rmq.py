import pika
import logging


class Connecter:
    """
    RMQ connecter
    """

    def __init__(self):
        self.connection = None

    def init_app(self, app):
        creds = pika.PlainCredentials(
            app.config.get('RMQ_USER'), app.config.get('RMQ_PASS')
        )

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            app.config.get('RMQ_HOST'), virtual_host=app.config.get("RMQ_VHOST"), credentials=creds)
        )

        self.channel = self.connection.channel()

    def define_queue(self, queue_name):
        self.channel.queue_declare(queue=queue_name)

    def listen(self, queue, callback):

        self.channel.basic_consume(queue=queue,
                                   auto_ack=True,
                                   on_message_callback=callback)
        logging.info(f' [*] Waiting for messages on {queue}. To exit press CTRL+C')
        self.channel.start_consuming()

    def produce(self, queue, message):
        self.channel.basic_publish('', routing_key=queue, body=message)
