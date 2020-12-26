const Joi = require('joi');

const Algorithm = require('../../algorithm');
const { getLogger } = require('../logger');
const { getMQ } = require('.');
const { imagingSchema } = require('../../schemas');

const logger = getLogger();

class MQOperations {
  constructor(inQueue) {
    this.channel = getMQ();
    this.algorithm = new Algorithm();

    this.inQueue = inQueue;

    this.FETCH_COUNT = 1;
    this.NO_ACK = false;
    this.REQUEUE_ON_REJECT = false;
  }

  _msgHandler(msg) {
    let imaging = {};

    try {
      imaging = JSON.parse(msg.content.toString());
      Joi.assert(imaging, imagingSchema);
      logger.info(`Consumed imaging ${imaging._id}`);

      this.algorithm.run(imaging);
      this.channel.ack(msg);
      logger.info(`Acked imaging ${imaging._id}`);
    }
    catch (err) {
      logger.error(err);
      this.channel.reject(msg, this.REQUEUE_ON_REJECT);
      logger.error(`Rejected imaging ${imaging._id} with requeue=${this.REQUEUE_ON_REJECT}`);
    }
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
