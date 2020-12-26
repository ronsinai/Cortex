from datetime import datetime
import json
import logging

from pconf import Pconf
from pino import pino

MILLIDIFF = False

def dump_function(json_log):
    json_log['hostname'] = json_log['host']
    json_log['msg'] = json_log['message']
    json_log['time'] = datetime.utcfromtimestamp(json_log['time']/1000) \
                               .isoformat(timespec='milliseconds') + 'Z'

    keys = ['level', 'time', 'hostname', 'msg']
    json_log = {key:json_log[key] for key in keys}

    if isinstance(json_log['msg'], Exception):
        json_log['msg'] = str(json_log['msg'])
        json_log['stack'] = logging.traceback.format_exc()

    return json.dumps(json_log)

logger = pino(
    level=Pconf.get().get('LOG_LEVEL'),
    millidiff=MILLIDIFF,
    dump_function=dump_function,
)

def get_logger():
    return logger
