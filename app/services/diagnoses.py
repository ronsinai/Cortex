from pconf import Pconf

from app.clients import Elef
from app.schemas import DiagnosisSchema
from app.utils.logger import get_logger

logger = get_logger()

class DiagnosesService:
    def __init__(self):
        self.elef = Elef(url=Pconf.get().get('ELEF_URI'))

    def post(self, diagnosis):
        try:
            DiagnosisSchema().load(diagnosis)
            logger.info(
                f"Posting {diagnosis.get('diagnosis')} diagnosis of "
                f"imaging {diagnosis.get('imagingId')} to 1000",
            )
            res = self.elef.post_diagnosis(diagnosis)
            res.raise_for_status()
            logger.info(
                f"Posted {diagnosis.get('diagnosis')} diagnosis of "
                f"imaging {diagnosis.get('imagingId')} to 1000",
            )

        except Exception as err:
            logger.info(
                f"Failed to post {diagnosis.get('diagnosis')} diagnosis of "
                f"imaging {diagnosis.get('imagingId')} to 1000",
            )
            raise err
