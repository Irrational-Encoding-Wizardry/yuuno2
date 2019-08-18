from asyncio import wait_for

from aiounittest import AsyncTestCase

from yuuno2.networking.base import Message
from yuuno2.networking.pipe import pipe_bidi
from yuuno2.networking.reqresp import ReqRespServer, ReqRespClient, function, CallFailed


class MockReqRespServer(ReqRespServer):

    async def on_echo(self, _buffers=None, **params) -> Message:
        if _buffers is None:
            _buffers = []

        return Message(params, _buffers)

    async def on_error(self) -> Message:
        raise RuntimeError("Generic Error.")


class MockReqRespClient(ReqRespClient):
    echo = function()
    error = function()
    non_existent = function()

class ReqRespServerTest(AsyncTestCase):
    async def test_invalid_packet__no_id(self):
        c1, c2 = pipe_bidi()
        srv = MockReqRespServer(c1)
        async with srv, c2:
            await c2.write(Message({'type': 'request', 'method': 'none', 'params': {}}))
            msg: Message = await wait_for(c2.read(), 5)

            self.assertIsInstance(msg.values, dict)
            self.assertIn('type', msg.values)
            self.assertEqual('error', msg.values['type'])
            self.assertIn('id', msg.values)
            self.assertIsNone(msg.values['id'])
            self.assertIn('error', msg.values)

    async def test_invalid_packet__unknown_type(self):
        c1, c2 = pipe_bidi()
        srv = MockReqRespServer(c1)
        async with srv, c2:
            await c2.write(Message({'id': 0, 'type': 'wtf', 'method': 'none', 'params': {}}))
            msg: Message = await wait_for(c2.read(), 5)

            self.assertIsInstance(msg.values, dict)
            self.assertIn('type', msg.values)
            self.assertEqual('error', msg.values['type'])
            self.assertIn('id', msg.values)
            self.assertEqual(0, msg.values['id'])
            self.assertIn('error', msg.values)
    async def test_invalid_packet__unset_method(self):
        c1, c2 = pipe_bidi()
        srv = MockReqRespServer(c1)
        async with srv, c2:
            await c2.write(Message({'id': 0, 'type': 'request', 'params': {}}))
            msg: Message = await wait_for(c2.read(), 5)

            self.assertIsInstance(msg.values, dict)
            self.assertIn('type', msg.values)
            self.assertEqual('error', msg.values['type'])
            self.assertIn('id', msg.values)
            self.assertEqual(0, msg.values['id'])
            self.assertIn('error', msg.values)

    async def test_valid_packet__echo(self):
        c1, c2 = pipe_bidi()
        srv = MockReqRespServer(c1)
        async with srv, c2:
            await c2.write(Message({'id': 0, 'type': 'request', 'method': 'echo', 'params': {}}))
            msg: Message = await wait_for(c2.read(), 5)

            self.assertIsInstance(msg.values, dict)
            self.assertIn('type', msg.values)
            self.assertEqual('response', msg.values['type'])
            self.assertIn('id', msg.values)
            self.assertEqual(0, msg.values['id'])
            self.assertIn('result', msg.values)
            self.assertIsInstance(msg.values['result'], dict)
            self.assertEqual(0, len(msg.values['result']))

    async def test_valid_packet__error(self):
        c1, c2 = pipe_bidi()
        srv = MockReqRespServer(c1)
        async with srv, c2:
            await c2.write(Message({'id': 0, 'type': 'request', 'method': 'error', 'params': {}}))
            msg: Message = await wait_for(c2.read(), 5)

            self.assertIsInstance(msg.values, dict)
            self.assertIn('type', msg.values)
            self.assertEqual('error', msg.values['type'])
            self.assertIn('id', msg.values)
            self.assertEqual(0, msg.values['id'])
            self.assertIn('error', msg.values)
            self.assertIn('Generic Error.', msg.values['error'])


class ReqRespClientTest(AsyncTestCase):

    async def test_echo(self):
        c1, c2 = pipe_bidi()
        srv = MockReqRespServer(c1)
        cli = MockReqRespClient(c2)

        async with srv, cli:
            result: Message = await wait_for(cli.echo(), 5)
            self.assertEqual(Message({}, []), result)

    async def test_error(self):
        c1, c2 = pipe_bidi()
        srv = MockReqRespServer(c1)
        cli = MockReqRespClient(c2)

        async with srv, cli:
            with self.assertRaises(CallFailed):
                await wait_for(cli.error(), 5)

    async def test_non_existent(self):
        c1, c2 = pipe_bidi()
        srv = MockReqRespServer(c1)
        cli = MockReqRespClient(c2)

        async with srv, cli:
            with self.assertRaises(CallFailed):
                await wait_for(cli.non_existent(), 5)
