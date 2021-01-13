from pconf import Pconf

from app.utils.logger import get_logger
import app.utils.mq as MQ
from app.utils.mq.operations import MQOperations

logger = get_logger()

class Consumer:
    async def start(self):
        try:
            await self._connect_to_mq()
        except Exception as err:
            logger.error(err)
            raise err

    async def _connect_to_mq(self):
        await MQ.connect(url=Pconf.get().get('AMQP_URI'))
        logger.info(f"Cortex : connected to rabbitmq at {Pconf.get().get('AMQP_URI')}")

        await MQ.assert_exchange(
            exchange=Pconf.get().get('AMQP_DEAD_EXCHANGE'),
            exchange_type=Pconf.get().get('AMQP_DEAD_EXCHANGE_TYPE'),
        )
        await MQ.set_up(
            exchange=Pconf.get().get('AMQP_IN_EXCHANGE'),
            exchange_type=Pconf.get().get('AMQP_IN_EXCHANGE_TYPE'),
            queue=Pconf.get().get('AMQP_IN_QUEUE'),
            patterns=Pconf.get().get('AMQP_IN_PATTERNS').split(' '),
            queue_args={
                'x-dead-letter-exchange': Pconf.get().get('AMQP_DEAD_EXCHANGE'),
                'x-dead-letter-routing-key': Pconf.get().get('AMQP_IN_QUEUE'),
            },
        )
        await MQ.assert_exchange(
            exchange=Pconf.get().get('AMQP_OUT_EXCHANGE'),
            exchange_type=Pconf.get().get('AMQP_OUT_EXCHANGE_TYPE'),
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
        await self.mq.consume()

    @staticmethod
    async def _close_mq_connection():
        await MQ.close()
        logger.info(f"Cortex : disconnected from rabbitmq at {Pconf.get().get('AMQP_URI')}")

    async def stop(self):
        try:
            await self._close_mq_connection()
        except Exception as err:
            logger.error(err)
            raise err

        logger.info('Cortex : shutting down')
