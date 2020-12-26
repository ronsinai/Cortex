from pconf import Pconf

from app.utils.logger import get_logger
import app.utils.mq as MQ
from app.utils.mq.operations import MQOperations

logger = get_logger()

class Consumer:
    def start(self):
        try:
            self.mq = None
            self._connect_to_mq()
        except Exception as err:
            logger.error(err)
            raise err

    def _connect_to_mq(self):
        MQ.connect(url=Pconf.get().get('AMQP_URI'))
        MQ.assert_exchange(
            exchange=Pconf.get().get('AMQP_EXCHANGE'),
            exchange_type=Pconf.get().get('AMQP_EXCHANGE_TYPE'),
        )
        MQ.assert_queue(queue=Pconf.get().get('AMQP_QUEUE'))
        MQ.bind_queue(
            queue=Pconf.get().get('AMQP_QUEUE'),
            exchange=Pconf.get().get('AMQP_EXCHANGE'),
            patterns=Pconf.get().get('patterns'),
        )
        logger.info(f"Cortex : connected to rabbitmq at {Pconf.get().get('AMQP_URI')}")

        self.mq = MQOperations(in_queue=Pconf.get().get('AMQP_QUEUE')) # pylint: disable=attribute-defined-outside-init

        logger.info(
            f"Cortex : consuming from {Pconf.get().get('AMQP_EXCHANGE')} exchange "
            f"through {Pconf.get().get('AMQP_QUEUE')} queue "
            f"with patterns: {Pconf.get().get('patterns')}",
        )
        self.mq.consume()

    def _close_mq_connection(self):
        if self.mq:
            self.mq.stop()
        MQ.close()
        logger.info(f"Cortex : disconnected from rabbitmq at {Pconf.get().get('AMQP_URI')}")

    def stop(self):
        try:
            self._close_mq_connection()
        except Exception as err:
            logger.error(err)
            raise err

        logger.info('Cortex : shutting down')
