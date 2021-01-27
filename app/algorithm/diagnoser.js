const Joi = require('joi');
const Nconf = require('nconf');

const { getLogger } = require('../utils/logger');
const { diagnosisSchema, imagingSchema } = require('../schemas');

const Diagnostics = require('../../diagnostics');

const logger = getLogger();

class Diagnoser {
  constructor() {
    this.diagnoser = Diagnostics;
  }

  // eslint-disable-next-line class-methods-use-this
  cleanEmpties(obj) {
    // eslint-disable-next-line no-param-reassign
    Object.keys(obj).forEach((k) => (!obj[k] && obj[k] !== undefined) && delete obj[k]);
  }

  run(imaging) {
    try {
      Joi.assert(imaging, imagingSchema);
      // eslint-disable-next-line object-curly-newline
      const { _id, type, bodyPart, metadata, path } = imaging;
      const { age, sex } = metadata;
      logger.info(`Diagnosing imaging ${_id} of ${bodyPart} ${type} of ${age}y ${sex} at ${path}`);

      const diagnosisDefault = { imagingId: _id, imagingType: type, diagnosis: Nconf.get('AMQP_IN_QUEUE') };
      const diagnosisAlgorithm = this.diagnoser.diagnose(imaging);
      this.cleanEmpties(diagnosisAlgorithm);

      const diagnosis = { ...diagnosisDefault, ...diagnosisAlgorithm };
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
