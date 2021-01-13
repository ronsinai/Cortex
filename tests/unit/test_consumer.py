import json
import pytest
import unittest.mock

from tests.utils.mq import get_message

class TestConsumer:
    @pytest.fixture(autouse=True)
    def run_around_tests(self, mocker, mq):
        self.algorithm_spy = mocker.spy(mq.algorithm, 'run')

        original_channel = mq.channel
        self.publish_mock = mq.channel.basic_publish = unittest.mock.MagicMock()
        self.ack_mock = mq.channel.basic_ack = unittest.mock.MagicMock()
        self.reject_mock = mq.channel.basic_reject = unittest.mock.MagicMock()
        yield
        mq.channel = original_channel

    @pytest.mark.asyncio
    async def test_ack_msg(self, event_loop, mq, example_imaging, example_diagnosis):
        msg = get_message(example_imaging)
        await mq._msg_handler(msg)

        self.algorithm_spy.assert_called_once_with(example_imaging)
        self.publish_mock.assert_called_once_with(
            exchange=unittest.mock.ANY,
            routing_key=unittest.mock.ANY,
            body=json.dumps(example_diagnosis).encode('utf-8'),
            properties=unittest.mock.ANY,
        )
        self.ack_mock.assert_called_once_with(delivery_tag=msg.delivery.delivery_tag)
        self.reject_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_reject_and_drop_msg_on_msg_error(self, mq, bad_imaging):
        msg = get_message(bad_imaging)
        await mq._msg_handler(msg)

        self.algorithm_spy.assert_not_called()
        self.publish_mock.assert_not_called()
        self.ack_mock.assert_not_called()
        self.reject_mock.assert_called_once_with(delivery_tag=msg.delivery.delivery_tag, requeue=False)

    @pytest.mark.asyncio
    async def test_reject_and_drop_msg_on_alg_error(self, mq, example_imaging):
        self.algorithm_mock = mq.algorithm.run = unittest.mock.MagicMock()
        self.algorithm_mock.side_effect = Exception()

        msg = get_message(example_imaging)
        await mq._msg_handler(msg)

        self.algorithm_mock.assert_called_once_with(example_imaging)
        self.publish_mock.assert_not_called()
        self.ack_mock.assert_not_called()
        self.reject_mock.assert_called_once_with(delivery_tag=msg.delivery.delivery_tag, requeue=False)

    @pytest.mark.asyncio
    async def test_reject_and_requeue_msg_on_pub_error(self, mq, example_imaging, example_diagnosis):
        self.publish_mock = mq.channel.basic_publish = unittest.mock.MagicMock()
        self.publish_mock.side_effect = Exception()

        msg = get_message(example_imaging)
        await mq._msg_handler(msg)

        self.algorithm_spy.assert_called_once_with(example_imaging)
        self.publish_mock.assert_called_once_with(
            exchange=unittest.mock.ANY,
            routing_key=unittest.mock.ANY,
            body=json.dumps(example_diagnosis).encode('utf-8'),
            properties=unittest.mock.ANY,
        )
        self.ack_mock.assert_not_called()
        self.reject_mock.assert_called_once_with(delivery_tag=msg.delivery.delivery_tag, requeue=True)
