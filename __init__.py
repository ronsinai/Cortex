from pconf import Pconf

Pconf.env()
Pconf.defaults({
    'PYTHON_ENV': 'dev',
    'LOG_LEVEL': 'info',
    'AMQP_URI': 'amqp://localhost:5672',
    'AMQP_IN_EXCHANGE': 'imagings',
    'AMQP_IN_EXCHANGE_TYPE': 'topic',
    'AMQP_IN_QUEUE': 'syringomyelia',
    'AMQP_IN_PATTERNS': 'MRI.spine.*',
    'AMQP_OUT_EXCHANGE': 'diagnoses',
    'AMQP_OUT_EXCHANGE_TYPE': 'direct',
    'AMQP_DEAD_EXCHANGE': 'diagnoses-error',
    'AMQP_DEAD_EXCHANGE_TYPE': 'direct',
})

from app import App # pylint: disable=wrong-import-position

app_instance = App()

try:
    app_instance.start()
except KeyboardInterrupt:
    app_instance.stop()
except Exception as err: # pylint: disable=broad-except
    app_instance.stop()
