import json
import pika

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

    def _publish(self, key, content):
        self.channel.publish(
            exchange=self.out_exchange,
            routing_key=key,
            body=json.dumps(content).encode('utf-8'),
            properties=pika.BasicProperties(
                delivery_mode=self.DELIVERY_MODE,
            ),
        )

    def _msg_handler(self, ch, method, _properties, body):
        imaging = {}
        diagnosis = {}

        try:
            imaging = json.loads(body.decode('utf-8'))
            ImagingSchema().load(imaging)
            logger.info(f"Consumed imaging {imaging.get('_id')}")

            diagnosis = self.algorithm.run(imaging)
        except Exception as err: # pylint: disable=broad-except
            logger.error(err)
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=self.REQUEUE_ON_ALG_ERR)
            return logger.error(f"Rejected imaging {imaging.get('_id')} with requeue={self.REQUEUE_ON_ALG_ERR}")

        try:
            routing_key = self._get_routing_key(diagnosis)
            self._publish(routing_key, diagnosis)
            logger.info(f"Published {diagnosis.get('diagnosis')} diagnosis of imaging {imaging.get('_id')} to {self.out_exchange} exchange")
        except Exception as err: # pylint: disable=broad-except
            logger.error(err)
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=self.REQUEUE_ON_PUB_ERR)
            return logger.error(f"Rejected imaging {imaging.get('_id')} with requeue={self.REQUEUE_ON_PUB_ERR}")

        ch.basic_ack(delivery_tag=method.delivery_tag)
        return logger.info(f"Acked imaging {imaging.get('_id')}")

    def consume(self):
        self.channel.basic_qos(prefetch_count=self.FETCH_COUNT)

        self.channel.basic_consume(queue=self.in_queue, on_message_callback=self._msg_handler)
        self.channel.start_consuming()

    def stop(self):
        self.channel.stop_consuming()
