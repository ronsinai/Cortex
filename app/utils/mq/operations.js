const Joi = require('joi');

const Algorithm = require('../../algorithm');
const { getLogger } = require('../logger');
const { getMQ } = require('.');
const { imagingSchema } = require('../../schemas');

const logger = getLogger();

class MQOperations {
  constructor(inQueue, outExchange, options = {}) {
    this.channel = getMQ();
    this.algorithm = new Algorithm();

    this.inQueue = inQueue;
    this.outExchange = outExchange;

    this.PERSISTENT = true;
    this.FETCH_COUNT = 1;
    this.NO_ACK = false;
    this.REQUEUE_ON_ALG_ERR = false;
    this.REQUEUE_ON_PUB_ERR = true;

    this.options = options;
    this.options.persistent = this.PERSISTENT;
  }

  // eslint-disable-next-line class-methods-use-this
  _getRoutingKey(diagnosis) {
    return `${diagnosis.diagnosis}`;
  }

  async _publish(key, content) {
    // eslint-disable-next-line max-len
    await this.channel.publish(this.outExchange, key, Buffer.from(JSON.stringify(content)), this.persistent);
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
      const routingKey = this._getRoutingKey(diagnosis);
      await this._publish(routingKey, diagnosis);
      logger.info(`Published ${diagnosis.diagnosis} diagnosis of imaging ${imaging._id} to ${this.outExchange} exchange`);
    }
    catch (err) {
      logger.error(err);
      this.channel.reject(msg, this.REQUEUE_ON_PUB_ERR);
      return logger.error(`Rejected imaging ${imaging._id} with requeue=${this.REQUEUE_ON_PUB_ERR}`);
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
