const Joi = require('joi');

const Algorithm = require('../../algorithm');
const { getMQ } = require('.');
const { imagingSchema } = require('../../schemas');

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
      console.info(`Consumed imaging ${imaging._id}`);

      this.algorithm.run(imaging);
      this.channel.ack(msg);
      console.info(`Acked imaging ${imaging._id}`);
    }
    catch (err) {
      console.error(err);
      this.channel.reject(msg, this.REQUEUE_ON_REJECT);
      console.error(`Rejected imaging ${imaging._id} with requeue=${this.REQUEUE_ON_REJECT}`);
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
