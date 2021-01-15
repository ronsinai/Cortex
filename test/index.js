const Nconf = require('nconf');

Nconf.use('memory');
Nconf.argv().env().defaults({
  NODE_ENV: 'test',
  LOG_LEVEL: 'silent',
  AMQP_URI: 'amqp://localhost:5672',
  AMQP_IN_EXCHANGE: 'test_imagings',
  AMQP_IN_EXCHANGE_TYPE: 'topic',
  AMQP_IN_QUEUE: 'test_syringomyelia',
  AMQP_IN_PATTERNS: 'MRI.spine.*',
  AMQP_OUT_EXCHANGE: 'test_diagnoses',
  AMQP_OUT_EXCHANGE_TYPE: 'direct',
});

const Consumer = require('../app');

before(async () => {
  global.consumerInstance = new Consumer();
  await global.consumerInstance.start();
});

after(async () => {
  await global.consumerInstance.stop();
});
