import aiormq
import asyncio

DURABLE = True

connection = None
channel = None

async def connect(url):
    global connection, channel # pylint: disable=global-statement
    if not channel:
        connection = await aiormq.connect(url=url)
        channel = await connection.channel()

    return channel

async def assert_exchange(exchange, exchange_type, args=None):
    await channel.exchange_declare(exchange=exchange, exchange_type=exchange_type, durable=DURABLE, arguments=args)

async def assert_queue(queue, args=None):
    await channel.queue_declare(queue=queue, durable=DURABLE, arguments=args)

async def bind_queue(queue, exchange, patterns):
    await asyncio.gather(
        *[channel.queue_bind(queue=queue, exchange=exchange, routing_key=pattern) for pattern in patterns]
    )

async def set_up(exchange, exchange_type, queue, patterns, exchange_args=None, queue_args=None):
    await assert_exchange(exchange, exchange_type, exchange_args)
    await assert_queue(queue, queue_args)
    await bind_queue(queue, exchange, patterns)

async def close():
    if channel:
        await channel.close()
    if connection:
        await connection.close()

def get_mq():
    return channel
