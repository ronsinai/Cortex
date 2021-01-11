const Joi = require('joi');
const Nconf = require('nconf');

const { getLogger } = require('../utils/logger');
const { diagnosisSchema, imagingSchema } = require('../schemas');

const logger = getLogger();

class Diagnoser {
  // eslint-disable-next-line class-methods-use-this
  run(imaging) {
    try {
      Joi.assert(imaging, imagingSchema);
      // eslint-disable-next-line object-curly-newline
      const { _id, type, bodyPart, metadata, path } = imaging;
      const { age, sex } = metadata;
      logger.info(`Diagnosing imaging ${_id} of ${bodyPart} ${type} of ${age}y ${sex} at ${path}`);

      const diagnosis = { imagingId: _id, imagingType: type, diagnosis: Nconf.get('AMQP_IN_QUEUE') };
      Joi.assert(diagnosis, diagnosisSchema);
      logger.info(`Diagnosed imaging ${_id} with ${Nconf.get('AMQP_IN_QUEUE')}`);
      return diagnosis;
    }
    catch (err) {
      logger.error(`Failed to diagnose imaging ${imaging._id}`);
      throw err;
    }
  }
}

module.exports = Diagnoser;
