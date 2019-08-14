from aiounittest import AsyncTestCase
from unittest import TestCase

from yuuno2.sans_io import *


class TestBuffer(TestCase):

    def test_feed_size_increasing(self):
        buf = Buffer()
        self.assertEqual(len(buf), 0)
        buf.feed(b'1')
        self.assertEqual(len(buf), 1)
        buf.feed(b'234')
        self.assertEqual(len(buf), 4)

    def test_read_full_blocks(self):
        buf = Buffer()
        buf.feed(b'1')
        buf.feed(b'123')
        self.assertEqual(buf.read(1), b'1')
        self.assertEqual(len(buf), 3)
        self.assertEqual(buf.read(3), b'123')
        self.assertEqual(len(buf), 0)

    def test_read_partial_blocks(self):
        buf = Buffer()

        buf.feed(b'abcdefghijklmnopqrstuvwxyz')
        buf.feed(b'1234567890')
        buf.feed(b'ABCDEFGH')

        # Partial at beginning of block.
        self.assertEqual(buf.read(5), b'abcde')

        # Partial at middle of block
        self.assertEqual(buf.read(10), b'fghijklmno')

        # Partial at end of block.
        self.assertEqual(buf.read(11), b'pqrstuvwxyz')
        self.assertEqual(buf.read(4), b'1234')

        # Partial inter-block
        self.assertEqual(buf.read(10), b'567890ABCD')

    def test_size_partial_blocks(self):
        buf = Buffer()

        buf.feed(b'abcdefghijklmnopqrstuvwxyz')
        buf.feed(b'1234567890')
        buf.feed(b'ABCDEFGH')

        self.assertEqual(len(buf), 26+10+8)
        buf.read(5)
        self.assertEqual(len(buf), (26 + 10 + 8) - (5))
        buf.read(10)
        self.assertEqual(len(buf), (26 + 10 + 8) - (5 + 10))
        buf.read(11)
        self.assertEqual(len(buf), (26 + 10 + 8) - (5 + 10 + 11))
        buf.read(4)
        self.assertEqual(len(buf), (26 + 10 + 8) - (5 + 10 + 11 + 4))

        buf.read(10)
        self.assertEqual(len(buf), (26 + 10 + 8) - (5 + 10 + 11 + 4 + 10))

    def test_peek(self):
        buf = Buffer()
        buf.feed(b'abc')
        buf.read(1)
        self.assertEqual(len(buf), 2)
        self.assertEqual(buf.peek(), buf.peek())
        self.assertEqual(len(buf.peek()), 2)

    def test_read_feed_interleave(self):
        buf = Buffer()
        buf.feed(b'abc')
        buf.read(1)
        self.assertEqual(buf.peek(), b"bc")
        buf.feed(b'defg')
        self.assertEqual(buf.peek(), b"bcdefg")
        buf.read(4)
        self.assertEqual(buf.peek(), b"fg")

    def test_read_closed(self):
        buf = Buffer()
        buf.feed(b'abc')
        buf.close()

        self.assertEqual(buf.read(4), b'abc')
        self.assertIsNone(buf.read(1))


class ConsumerTest(TestCase):

    def test_consumer_finish(self):
        @protocol
        async def _parser1():
            await sleep()

        @protocol
        async def _parser2():
            pass

        c1 = _parser1()
        self.assertFalse(c1.closed)
        list(c1.feed(b""))
        self.assertTrue(c1.closed)

        c2 = _parser2()
        self.assertTrue(c2.closed)

    def test_consumer_sleep(self):
        checkpoint_a = False
        checkpoint_b = False

        @protocol
        async def _parser():
            nonlocal checkpoint_a, checkpoint_b
            checkpoint_a = True
            await sleep()
            checkpoint_b = True

        consumer = _parser()
        self.assertTrue(checkpoint_a)
        self.assertFalse(checkpoint_b)
        list(consumer.feed(b""))
        self.assertTrue(checkpoint_a)
        self.assertTrue(checkpoint_b)

    def test_consumer_exception(self):
        @protocol
        async def _parser():
            await sleep()
            raise Exception("Test")

        consumer = _parser()
        with self.assertRaises(Exception):
            list(consumer.feed(b""))

    def test_consumer_emit(self):
        v1 = object()

        @protocol
        async def _parser():
            await sleep()
            await emit(v1)

        consumer = _parser()
        lst = list(consumer.feed(b""))
        self.assertEqual(len(lst), 1)
        self.assertIs(lst[0], v1)

    def test_consumer_read(self):
        @protocol
        async def _parser():
            await sleep()
            await emit(await read())

        consumer = _parser()
        self.assertEqual(next(iter(consumer.feed(b"123"))), b"123")

    def test_consumer_peek(self):
        @protocol
        async def _parser():
            await sleep()
            self.assertEqual(await peek(), b"123")
            await sleep()
            self.assertEqual(await peek(), b"123456")

        consumer = _parser()
        list(consumer.feed(b"123"))
        list(consumer.feed(b"456"))

    def test_consumer_left(self):
        @protocol
        async def _parser():
            await sleep()
            self.assertEqual(await left(), 3)
            await sleep()
            self.assertEqual(await left(), 6)

        consumer = _parser()
        list(consumer.feed(b"123"))
        list(consumer.feed(b"456"))

    def test_consumer_close(self):
        @protocol
        async def _parser():
            await sleep()
            await close()

        consumer = _parser()
        list(consumer.feed(b""))
        self.assertTrue(consumer.closed)

    def test_consumer_closing(self):
        @protocol
        async def _parser():
            await sleep()
            await close()
            self.assertTrue(await closing())

        consumer = _parser()
        list(consumer.feed(b""))

    def test_consumer_wait(self):
        @protocol
        async def _parser():
            await wait(10)
            self.assertGreaterEqual(await left(), 10)

        consumer = _parser()
        list(consumer.feed(b"12345"))
        self.assertFalse(consumer.closed)
        list(consumer.feed(b"1234"))
        self.assertFalse(consumer.closed)
        list(consumer.feed(b"1"))
        self.assertTrue(consumer.closed)

    def test_consumer_read_exactly(self):
        @protocol
        async def _parser():
            await emit(await read_exactly(10))

        consumer = _parser()
        self.assertEqual(list(consumer.feed(b"12345")), [])
        self.assertEqual(list(consumer.feed(b"1234")), [])
        self.assertEqual(list(consumer.feed(b"12")), [b"1234512341"])
