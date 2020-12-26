const Joi = require('joi');
const Nconf = require('nconf');

const { imagingSchema } = require('../schemas');

class Diagnoser {
  // eslint-disable-next-line class-methods-use-this
  run(imaging) {
    try {
      Joi.assert(imaging, imagingSchema);
      // eslint-disable-next-line object-curly-newline
      const { _id, type, bodyPart, metadata, path } = imaging;
      const { age, sex } = metadata;
      console.info(`Diagnosing imaging ${_id} of ${bodyPart} ${type} of ${age}y ${sex} at ${path}`);

      const diagnosis = { imagingId: _id, imagingType: type, diagnosis: Nconf.get('AMQP_QUEUE') };
      console.info(`Diagnosed imaging ${_id} with ${Nconf.get('AMQP_QUEUE')}`);
      return diagnosis;
    }
    catch (err) {
      console.error(`Failed to diagnose imaging ${imaging._id}`);
      throw err;
    }
  }
}

module.exports = Diagnoser;
