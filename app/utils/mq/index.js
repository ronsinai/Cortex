const Amqp = require('amqplib');

const DURABLE = true;

let connection;
let channel;

const connect = async (url) => {
  if (!channel) {
    connection = await Amqp.connect(url);
    channel = await connection.createChannel();
  }

  return channel;
};

const assertQueue = async (queue, options = {}) => {
  // eslint-disable-next-line no-param-reassign
  options.durable = DURABLE;
  await channel.assertQueue(queue, options);
};

const close = async () => {
  await channel.close();
  await connection.close();
};

const getMQ = () => channel;

module.exports = {
  connect,
  assertQueue,
  close,
  getMQ,
};
