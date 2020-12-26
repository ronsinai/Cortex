const Nconf = require('nconf');

const MQ = require('./utils/mq');
const MQOperations = require('./utils/mq/operations');

class App {
  async start() {
    try {
      await this._connectToMQ();
    }
    catch (err) {
      console.error(err);
      throw err;
    }
  }

  // eslint-disable-next-line class-methods-use-this
  async _connectToMQ() {
    await MQ.connect(Nconf.get('AMQP_URI'));
    await MQ.assertQueue(Nconf.get('AMQP_QUEUE'));
    console.info(`Cortex : connected to rabbitmq at ${Nconf.get('AMQP_URI')}`);

    this.mq = new MQOperations(Nconf.get('AMQP_QUEUE'));
    console.info(`Cortex : consuming from ${Nconf.get('AMQP_QUEUE')} queue`);
    await this.mq.consume();
  }

  // eslint-disable-next-line class-methods-use-this
  async _closeMQConnection() {
    await MQ.close();
    console.info(`Cortex : disconnected from rabbitmq at ${Nconf.get('AMQP_URI')}`);
  }

  async stop() {
    try {
      await this._closeMQConnection();
    }
    catch (err) {
      console.error(err);
      throw err;
    }
    console.info('Cortex : shutting down');
  }
}

module.exports = App;
