const Nconf = require('nconf');
const Process = require('process');

Nconf.use('memory');
Nconf.argv().env().defaults({
  NODE_ENV: 'dev',
  LOG_LEVEL: 'info',
  ELEF_URI: 'http://localhost:1995',
  AMQP_URI: 'amqp://localhost:5672',
  AMQP_EXCHANGE: 'imagings',
  AMQP_EXCHANGE_TYPE: 'topic',
  AMQP_QUEUE: 'syringomyelia',
  AMQP_PATTERNS: 'MRI.spine.*',
});

const App = require('./app');

const appInstance = new App();
appInstance.shutdown = async () => {
  await appInstance.stop();
};

Process.on('SIGINT', appInstance.shutdown);
Process.on('SIGTERM', appInstance.shutdown);

(async () => {
  try {
    await appInstance.start();
  }
  catch (err) {
    await appInstance.stop();
  }
})();
