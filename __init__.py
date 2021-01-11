from pconf import Pconf

Pconf.env()
Pconf.defaults({
    'PYTHON_ENV': 'dev',
    'LOG_LEVEL': 'info',
    'ELEF_URI': 'http://localhost:1995',
    'AMQP_URI': 'amqp://localhost:5672',
    'AMQP_EXCHANGE': 'imagings',
    'AMQP_EXCHANGE_TYPE': 'topic',
    'AMQP_QUEUE': 'syringomyelia',
    'AMQP_PATTERNS': 'MRI.spine.*',
})

from app import App # pylint: disable=wrong-import-position

app_instance = App()

try:
    app_instance.start()
except KeyboardInterrupt:
    app_instance.stop()
except Exception as err: # pylint: disable=broad-except
    app_instance.stop()
