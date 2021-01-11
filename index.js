const Nconf = require('nconf');
const Process = require('process');

Nconf.use('memory');
Nconf.argv().env().defaults({
  NODE_ENV: 'dev',
  LOG_LEVEL: 'info',
  AMQP_URI: 'amqp://localhost:5672',
  AMQP_IN_EXCHANGE: 'imagings',
  AMQP_IN_EXCHANGE_TYPE: 'topic',
  AMQP_IN_QUEUE: 'syringomyelia',
  AMQP_IN_PATTERNS: 'MRI.spine.*',
  AMQP_OUT_EXCHANGE: 'diagnoses',
  AMQP_OUT_EXCHANGE_TYPE: 'direct',
  AMQP_DEAD_EXCHANGE: 'diagnoses-error',
  AMQP_DEAD_EXCHANGE_TYPE: 'direct',
  AMQP_DEAD_QUEUE: 'diagnoses-error',
  AMQP_DEAD_PATTERNS: 'fracture infection pneumonia multiple_sclerosis syringomyelia stroke tumor gallbladder_disease prostate_problem synovitis',
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
