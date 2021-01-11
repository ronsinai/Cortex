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

def assert_exchange(exchange, exchange_type):
    channel.exchange_declare(exchange=exchange, exchange_type=exchange_type, durable=DURABLE)

def assert_queue(queue):
    channel.queue_declare(queue=queue, durable=DURABLE)

def bind_queue(queue, exchange, patterns):
    for pattern in patterns:
        channel.queue_bind(queue=queue, exchange=exchange, routing_key=pattern)

def set_up(exchange, exchange_type, queue, patterns):
    assert_exchange(exchange, exchange_type)
    assert_queue(queue)
    bind_queue(queue, exchange, patterns)

def close():
    if channel:
        channel.close()
    if connection:
        connection.close()

def get_mq():
    return channel
