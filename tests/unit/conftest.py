import json
import os
import pytest
import unittest.mock

from pconf import Pconf

async def async_magic():
    pass

unittest.mock.MagicMock.__await__ = lambda x: async_magic().__await__()

example_imaging_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/imaging.json')
_example_imaging = json.loads(open(example_imaging_path, 'r').read())

@pytest.fixture(scope='session', autouse=True)
def mq():
    return pytest.app.mq

@pytest.fixture(scope='session', autouse=True)
def algorithm():
    return pytest.app.mq.algorithm

@pytest.fixture(scope='session', autouse=True)
def example_imaging():
    return _example_imaging

@pytest.fixture(scope='session', autouse=True)
def bad_imaging():
    return {'_id': 'partial'}

@pytest.fixture(scope='session', autouse=True)
def example_diagnosis():
    return {
        'imagingId': _example_imaging.get('_id'),
        'imagingType': _example_imaging['type'],
        'diagnosis': Pconf.get()['AMQP_IN_QUEUE'],
    }

@pytest.fixture(scope='session', autouse=True)
def bad_diagnosis():
    return {'imagingId': 'partial'}
