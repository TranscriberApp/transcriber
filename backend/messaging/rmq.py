import logging

import pika


class Connecter:
    """
    RMQ connecter
    """

    def __init__(self):
        self.connection = None

    def _connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            self.host, virtual_host=self.vhost, credentials=self.creds)
        )

    def init_app(self, app):
        creds = pika.PlainCredentials(
            app.config.get('RMQ_USER'), app.config.get('RMQ_PASS')
        )
        self.creds = creds
        self.host = app.config.get('RMQ_HOST')
        self.vhost = app.config.get("RMQ_VHOST")

        self._connect()

    def define_queue(self, queue_name):
        channel = self.connection.channel()
        channel.queue_declare(queue=queue_name)

    def listen(self, queue, callback):
        self._connect()
        channel = self.connection.channel()
        channel.basic_consume(queue=queue,
                              auto_ack=True,
                              on_message_callback=callback)
        logging.info(
            f' [*] Waiting for messages on {queue}. To exit press CTRL+C')
        channel.start_consuming()

    def produce(self, queue, message, propdict=None):
        self._connect()
        if propdict is None:
            propdict = dict()
        props = pika.BasicProperties(headers=propdict)
        channel = self.connection.channel()
        channel.basic_publish('', routing_key=queue,
                              body=message, properties=props)
