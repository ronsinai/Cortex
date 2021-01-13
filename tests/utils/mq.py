import json

from dotmap import DotMap

def get_message(content):
    message = DotMap()
    message.body = json.dumps(content).encode('utf-8')
    message.delivery.delivery_tag = 1
    return message
