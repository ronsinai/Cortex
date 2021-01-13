import asyncio

from pconf import Pconf
import pytest
import uvloop

uvloop.install()

Pconf.env()
Pconf.defaults({
    'PYTHON_ENV': 'test',
    'LOG_LEVEL': 'critical',
    'AMQP_URI': 'amqp://localhost:5672',
    'AMQP_IN_EXCHANGE': 'test_imagings',
    'AMQP_IN_EXCHANGE_TYPE': 'topic',
    'AMQP_IN_QUEUE': 'test_syringomyelia',
    'AMQP_IN_PATTERNS': 'MRI.spine.*',
    'AMQP_OUT_EXCHANGE': 'test_diagnoses',
    'AMQP_OUT_EXCHANGE_TYPE': 'direct',
    'AMQP_DEAD_EXCHANGE': 'test_diagnoses-error',
    'AMQP_DEAD_EXCHANGE_TYPE': 'direct',
})

from app import App # pylint: disable=wrong-import-position

app_instance = App()
loop = asyncio.get_event_loop()

@pytest.fixture
def event_loop():
    return loop

def pytest_configure(config):
    pytest.app = app_instance
    loop.run_until_complete(app_instance.start())

def pytest_unconfigure(config):
    loop.run_until_complete(app_instance.stop())
    loop.close()
