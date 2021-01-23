import asyncio
import signal

from pconf import Pconf
import uvloop

uvloop.install()

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

def shutdown(_signal, loop): # pylint: disable=redefined-outer-name
    loop.stop()

def main():
    app_instance = App()
    loop = asyncio.get_event_loop()

    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(s, lambda s=s: shutdown(s, loop))

    try:
        loop.run_until_complete(app_instance.start())
        loop.run_forever()
    except: # pylint: disable=bare-except
        pass
    finally:
        loop.run_until_complete(app_instance.stop())
        loop.close()

if __name__ == '__main__':
    main()
