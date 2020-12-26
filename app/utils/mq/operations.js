const Joi = require('joi');

const Algorithm = require('../../algorithm');
const { DiagnosesService } = require('../../services');
const { getLogger } = require('../logger');
const { getMQ } = require('.');
const { imagingSchema } = require('../../schemas');

const logger = getLogger();

class MQOperations {
  constructor(inQueue) {
    this.channel = getMQ();
    this.algorithm = new Algorithm();
    this.diagnosesService = new DiagnosesService();

    this.inQueue = inQueue;

    this.FETCH_COUNT = 1;
    this.NO_ACK = false;
    this.REQUEUE_ON_ALG_ERR = false;
    this.REQUEUE_ON_SERVE_ERR = true;
  }

  async _msgHandler(msg) {
    let imaging = {};
    let diagnosis = {};

    try {
      imaging = JSON.parse(msg.content.toString());
      Joi.assert(imaging, imagingSchema);
      logger.info(`Consumed imaging ${imaging._id}`);

      diagnosis = this.algorithm.run(imaging);
    }
    catch (err) {
      logger.error(err);
      this.channel.reject(msg, this.REQUEUE_ON_ALG_ERR);
      return logger.error(`Rejected imaging ${imaging._id} with requeue=${this.REQUEUE_ON_ALG_ERR}`);
    }

    try {
      await this.diagnosesService.post(diagnosis);
    }
    catch (err) {
      logger.error(err);
      this.channel.reject(msg, this.REQUEUE_ON_SERVE_ERR);
      return logger.error(`Rejected imaging ${imaging._id} with requeue=${this.REQUEUE_ON_SERVE_ERR}`);
    }

    this.channel.ack(msg);
    return logger.info(`Acked imaging ${imaging._id}`);
  }

  async consume() {
    await this.channel.prefetch(this.FETCH_COUNT);

    await this.channel.consume(
      this.inQueue,
      this._msgHandler.bind(this),
      { noAck: this.NO_ACK },
    );
  }
}

module.exports = MQOperations;
