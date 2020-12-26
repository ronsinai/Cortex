from pconf import Pconf

Pconf.env()
Pconf.defaults({
    'PYTHON_ENV': 'dev',
    'LOG_LEVEL': 'INFO',
    'AMQP_URI': 'amqp://localhost:5672',
    'AMQP_QUEUE': 'syringomyelia',
})

from app import App # pylint: disable=wrong-import-position

app_instance = App()

try:
    app_instance.start()
except KeyboardInterrupt:
    app_instance.stop()
except Exception as err: # pylint: disable=broad-except
    app_instance.stop()
