from operator import itemgetter

from pconf import Pconf

from app.schemas import DiagnosisSchema, ImagingSchema
from app.utils.logger import get_logger

import diagnostics

logger = get_logger()

class Diagnoser:
    def __init__(self):
        self.diagnoser = diagnostics.initialize()

    @staticmethod
    def _prepare_for_matlab(data):
        keys = data.keys()
        for key in keys:
            if key[0] == '_' and key[1:] in keys:
                raise Exception(f"Conflicting imaging fields with: {key}")

        return {(key[1:] if key[0] == '_' else key):val for key, val in data.items()}

    def run(self, imaging):
        try:
            ImagingSchema().load(imaging)
            _id, type_, bodyPart, metadata, path = itemgetter('_id', 'type', 'bodyPart', 'metadata', 'path')(imaging)
            age, sex = itemgetter('age', 'sex')(metadata)
            logger.info(f"Diagnosing imaging {_id} of {bodyPart} {type_} of {age}y {sex} at {path}")

            imaging = self._prepare_for_matlab(imaging)
            diagnosis_default = {'imagingId': _id, 'imagingType': type_, 'diagnosis': Pconf.get().get('AMQP_IN_QUEUE')}
            diagnosis_algorithm = self.diagnoser.diagnose(imaging)

            diagnosis = {**diagnosis_default, **diagnosis_algorithm}
            DiagnosisSchema().load(diagnosis)
            logger.info(f"Diagnosed imaging {_id} with {Pconf.get().get('AMQP_IN_QUEUE')}")
            return diagnosis

        except Exception as err:
            logger.error(f"Failed to diagnose imaging {imaging.get('_id')}")
            raise err
