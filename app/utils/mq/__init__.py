import pika

DURABLE = True

connection = None
channel = None

def connect(url):
    global connection, channel # pylint: disable=global-statement
    if not channel:
        connection = pika.BlockingConnection(pika.URLParameters(url=url))
        channel = connection.channel()

    return channel

def assert_queue(queue):
    channel.queue_declare(queue=queue, durable=DURABLE)

def close():
    if channel:
        channel.close()
    if connection:
        connection.close()

def get_mq():
    return channel
