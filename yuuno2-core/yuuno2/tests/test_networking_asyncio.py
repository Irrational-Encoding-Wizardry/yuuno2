import socket
from asyncio import get_running_loop, open_connection, wait_for

from aiounittest import AsyncTestCase

from yuuno2.networking.asyncio import YuunoProtocol, ConnectionInputStream, ConnectionOutputStream
from yuuno2.networking.base import Message
from yuuno2.networking.serializer import ByteOutputStream


class FakeClosable:
    close = lambda self: None


class TestAsyncioProtocol(AsyncTestCase):

    async def test_read_stream(self):
        rsock, wsock = socket.socketpair()
        rt = None

        try:
            loop = get_running_loop()
            rt, proto = await loop.create_connection(YuunoProtocol, sock=rsock)
            stream = ConnectionInputStream(proto)

            wsock.sendall(ByteOutputStream.write_message(Message({"test": id(self)}, [])))

            async with stream:
                msg = await wait_for(stream.read(), 5)
                self.assertEqual(msg, Message({"test": id(self)}, []))

                wsock.shutdown(socket.SHUT_RDWR)
                await wait_for(stream.read(), 5)
                self.assertFalse(stream.acquired)

        finally:
            if rt is not None:
                rt.close()
            wsock.close()

    async def test_write_stream(self):
        rsock, wsock = socket.socketpair()
        wt = FakeClosable()
        rs_w = FakeClosable()

        try:
            rs_r, rs_w = await open_connection(sock=rsock)
            wt, wp = await get_running_loop().create_connection(YuunoProtocol, sock=wsock)

            wpos = ConnectionOutputStream(wp)
            async with wpos:
                msg = Message({"test": id(self)}, [])
                msg_raw = ByteOutputStream.write_message(msg)
                plength = len(msg_raw)

                await wait_for(wpos.write(msg), 5)
                data = await wait_for(rs_r.readexactly(plength), 5)
                self.assertEqual(data, msg_raw)

            await wait_for(rs_r.read(1), 5)
            self.assertTrue(rs_r.at_eof())

        finally:
            rs_w.close()
            wt.close()
