import json

from app.algorithm import Algorithm
from app.schemas import ImagingSchema
from app.services import DiagnosesService
from app.utils.logger import get_logger
from app.utils.mq import get_mq

logger = get_logger()

class MQOperations:
    def __init__(self, in_queue):
        self.channel = get_mq()
        self.algorithm = Algorithm()
        self.diagnoses_service = DiagnosesService()

        self.in_queue = in_queue

        self.FETCH_COUNT = 1
        self.NO_ACK = False
        self.REQUEUE_ON_ALG_ERR = False
        self.REQUEUE_ON_SERVE_ERR = True

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
            self.diagnoses_service.post(diagnosis)
        except Exception as err: # pylint: disable=broad-except
            logger.error(err)
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=self.REQUEUE_ON_SERVE_ERR)
            return logger.error(f"Rejected imaging {imaging.get('_id')} with requeue={self.REQUEUE_ON_SERVE_ERR}")

        ch.basic_ack(delivery_tag=method.delivery_tag)
        return logger.info(f"Acked imaging {imaging.get('_id')}")

    def consume(self):
        self.channel.basic_qos(prefetch_count=self.FETCH_COUNT)

        self.channel.basic_consume(queue=self.in_queue, on_message_callback=self._msg_handler)
        self.channel.start_consuming()

    def stop(self):
        self.channel.stop_consuming()
