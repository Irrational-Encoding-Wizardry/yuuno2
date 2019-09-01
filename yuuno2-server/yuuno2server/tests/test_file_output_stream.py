import os
from threading import Timer
from asyncio import wait_for
from unittest import TestCase, skip

from aiounittest import AsyncTestCase

from yuuno2.networking.base import Message
from yuuno2.networking.serializer import ByteOutputStream
from yuuno2.tests.utils import timeout_context
from yuuno2server.streams import FileOutputStream, FileInputStream


def pipe():
    r, w = os.pipe()
    return os.fdopen(r, "rb"), os.fdopen(w, "wb")


class TestFileOutputStream(AsyncTestCase):

    async def test_pipe_send(self):
        r, w = pipe()
        with r, w:
            fos = FileOutputStream(w)
            async with fos:
                await wait_for(fos.send(b"abc"), 5)
                self.assertEqual(r.read(3), b"abc")

    async def test_pipe_close(self):
        r, w = pipe()
        with r, w:
            fos = FileOutputStream(w)
            async with fos:
                await wait_for(fos.close(), 5)
                self.assertEqual(r.read(1), b"")
                self.assertTrue(w.closed)


class TestFileInputStream(AsyncTestCase):

    async def test_pipe_read(self):
        r, w = pipe()
        with r, w:
            fis = FileInputStream(r)
            async with timeout_context(fis, 5):
                msg = Message({"test": id(self)}, [])
                w.write(ByteOutputStream.write_message(msg))
                w.flush()
                self.assertEqual(await wait_for(fis.read(), 5), msg)

    async def test_pipe_close_while_read(self):
        r, w = pipe()
        with r, w:
            fis = FileInputStream(r)
            async with timeout_context(fis, 5):
                Timer(1, lambda: w.close()).start()
                self.assertEqual(await wait_for(fis.read(), 5), None)
