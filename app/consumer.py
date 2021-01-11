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
        logger.info(f"Cortex : connected to rabbitmq at {Pconf.get().get('AMQP_URI')}")

        MQ.set_up(
            exchange=Pconf.get().get('AMQP_IN_EXCHANGE'),
            exchange_type=Pconf.get().get('AMQP_IN_EXCHANGE_TYPE'),
            queue=Pconf.get().get('AMQP_IN_QUEUE'),
            patterns=Pconf.get().get('AMQP_IN_PATTERNS').split(' '),
        )
        MQ.set_up(
            exchange=Pconf.get().get('AMQP_OUT_EXCHANGE'),
            exchange_type=Pconf.get().get('AMQP_OUT_EXCHANGE_TYPE'),
            queue=Pconf.get().get('AMQP_OUT_QUEUE'),
            patterns=Pconf.get().get('AMQP_OUT_PATTERNS').split(' '),
        )

        self.mq = MQOperations( # pylint: disable=attribute-defined-outside-init
            in_queue=Pconf.get().get('AMQP_IN_QUEUE'),
            out_exchange=Pconf.get().get('AMQP_OUT_EXCHANGE'),
        )

        logger.info(
            f"Cortex : consuming from {Pconf.get().get('AMQP_IN_EXCHANGE')} exchange "
            f"through {Pconf.get().get('AMQP_IN_QUEUE')} queue "
            f"with patterns: {Pconf.get().get('AMQP_IN_PATTERNS').split(' ')}",
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
