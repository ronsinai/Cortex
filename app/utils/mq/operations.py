import json

import aiormq
from pconf import Pconf

from app.algorithm import Algorithm
from app.schemas import ImagingSchema
from app.utils.logger import get_logger
from app.utils.mq import get_mq

logger = get_logger()

class MQOperations:
    def __init__(self, in_queue, out_exchange):
        self.channel = get_mq()
        self.algorithm = Algorithm()

        self.in_queue = in_queue
        self.out_exchange = out_exchange

        self.DELIVERY_MODE = 2
        self.FETCH_COUNT = 1
        self.NO_ACK = False
        self.REQUEUE_ON_ALG_ERR = False
        self.REQUEUE_ON_PUB_ERR = True

    @staticmethod
    def _get_routing_key(diagnosis):
        return f"{diagnosis.get('diagnosis')}"

    async def _publish(self, key, content):
        await self.channel.basic_publish(
            exchange=self.out_exchange,
            routing_key=key,
            body=json.dumps(content).encode('utf-8'),
            properties=aiormq.spec.Basic.Properties(
                delivery_mode=self.DELIVERY_MODE,
            ),
        )

    async def _msg_handler(self, message):
        imaging = {}
        diagnosis = {}

        try:
            imaging = json.loads(message.body.decode('utf-8'))
            ImagingSchema().load(imaging)
            logger.info(f"Consumed imaging {imaging.get('_id')}")

            diagnosis = self.algorithm.run(imaging)
        except Exception as err: # pylint: disable=broad-except
            logger.error(err)
            await self.channel.basic_reject(delivery_tag=message.delivery.delivery_tag, requeue=self.REQUEUE_ON_ALG_ERR)
            
            dead_log = f" to {Pconf.get().get('AMQP_DEAD_EXCHANGE')} exchange" if self.REQUEUE_ON_ALG_ERR else ''
            return logger.error(f"Rejected imaging {imaging.get('_id')} with requeue={self.REQUEUE_ON_ALG_ERR}{dead_log}")

        try:
            routing_key = self._get_routing_key(diagnosis)
            await self._publish(routing_key, diagnosis)
            logger.info(f"Published {diagnosis.get('diagnosis')} diagnosis of imaging {imaging.get('_id')} to {self.out_exchange} exchange")
        except Exception as err: # pylint: disable=broad-except
            logger.error(err)
            await self.channel.basic_reject(delivery_tag=message.delivery.delivery_tag, requeue=self.REQUEUE_ON_PUB_ERR)
            
            dead_log = f" to {Pconf.get().get('AMQP_DEAD_EXCHANGE')} exchange" if self.REQUEUE_ON_PUB_ERR else ''
            return logger.error(f"Rejected imaging {imaging.get('_id')} with requeue={self.REQUEUE_ON_PUB_ERR}{dead_log}")

        await self.channel.basic_ack(delivery_tag=message.delivery.delivery_tag)
        return logger.info(f"Acked imaging {imaging.get('_id')}")

    async def consume(self):
        await self.channel.basic_qos(prefetch_count=self.FETCH_COUNT)
        await self.channel.basic_consume(queue=self.in_queue, consumer_callback=self._msg_handler)
