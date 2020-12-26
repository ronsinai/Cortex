from operator import itemgetter

from pconf import Pconf

from app.schemas import ImagingSchema
from app.utils.logger import get_logger

logger = get_logger()

class Diagnoser:
    @staticmethod
    def run(imaging):
        try:
            ImagingSchema().load(imaging)
            _id, type_, bodyPart, metadata, path = itemgetter('_id', 'type', 'bodyPart', 'metadata', 'path')(imaging)
            age, sex = itemgetter('age', 'sex')(metadata)
            logger.info(f"Diagnosing imaging {_id} of {bodyPart} {type_} of {age}y {sex} at {path}")

            diagnosis = {'imagingId': _id, 'imagingType': type_, 'diagnosis': Pconf.get().get('AMQP_QUEUE')}
            logger.info(f"Diagnosed imaging {_id} with {Pconf.get().get('AMQP_QUEUE')}")
            return diagnosis

        except Exception as err:
            logger.error(f"Failed to diagnose imaging {imaging.get('_id')}")
            raise err
