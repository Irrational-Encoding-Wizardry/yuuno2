from aiounittest import AsyncTestCase
from unittest import TestCase

from yuuno2.sans_io import Buffer


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