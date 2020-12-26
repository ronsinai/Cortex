const Nconf = require('nconf');

Nconf.use('memory');
Nconf.argv().env().defaults({
  NODE_ENV: 'test',
  LOG_LEVEL: 'silent',
  AMQP_URI: 'amqp://localhost:5672',
  AMQP_QUEUE: 'test_syringomyelia',
});

const Consumer = require('../app');

before(async () => {
  global.consumerInstance = new Consumer();
  await global.consumerInstance.start();
});

after(async () => {
  await global.consumerInstance.stop();
});
