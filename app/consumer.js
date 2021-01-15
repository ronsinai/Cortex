const Nconf = require('nconf');

const { getLogger } = require('./utils/logger');
const MQ = require('./utils/mq');
const MQOperations = require('./utils/mq/operations');

const logger = getLogger();

class App {
  async start() {
    try {
      await this._connectToMQ();
    }
    catch (err) {
      logger.error(err);
      throw err;
    }
  }

  // eslint-disable-next-line class-methods-use-this
  async _connectToMQ() {
    await MQ.connect(Nconf.get('AMQP_URI'));
    logger.info(`Cortex : connected to rabbitmq at ${Nconf.get('AMQP_URI')}`);

    await MQ.setUp(
      Nconf.get('AMQP_IN_EXCHANGE'),
      Nconf.get('AMQP_IN_EXCHANGE_TYPE'),
      Nconf.get('AMQP_IN_QUEUE'),
      Nconf.get('AMQP_IN_PATTERNS').split(' '),
    );
    await MQ.assertExchange(
      Nconf.get('AMQP_OUT_EXCHANGE'),
      Nconf.get('AMQP_OUT_EXCHANGE_TYPE'),
    );

    this.mq = new MQOperations(
      Nconf.get('AMQP_IN_QUEUE'),
      Nconf.get('AMQP_OUT_EXCHANGE'),
    );

    logger.info(
      `Cortex : `
      + `consuming from ${Nconf.get('AMQP_IN_EXCHANGE')} exchange through ${Nconf.get('AMQP_IN_QUEUE')} queue `
      + `with patterns: ['${Nconf.get('AMQP_IN_PATTERNS').split(' ').join("', '")}']`,
    );
    await this.mq.consume();
  }

  // eslint-disable-next-line class-methods-use-this
  async _closeMQConnection() {
    await MQ.close();
    logger.info(`Cortex : disconnected from rabbitmq at ${Nconf.get('AMQP_URI')}`);
  }

  async stop() {
    try {
      await this._closeMQConnection();
    }
    catch (err) {
      logger.error(err);
      throw err;
    }
    logger.info('Cortex : shutting down');
  }
}

module.exports = App;
