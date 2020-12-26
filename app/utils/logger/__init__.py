import logging

from pconf import Pconf

LOG_LEVEL = getattr(logging, Pconf.get().get('LOG_LEVEL'))
logging.basicConfig(format='%(message)s', level=LOG_LEVEL)
logging.getLogger('pika').setLevel(logging.WARNING)
logger = logging.getLogger()

def get_logger():
    return logger
