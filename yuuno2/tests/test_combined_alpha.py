from typing import Mapping, Union

from aiounittest import AsyncTestCase

from yuuno2.typings import Buffer
from yuuno2.format import RawFormat, RGB24, GRAY8, Size, RGBA32
from yuuno2.tests.mocks import MockFrame, MockClip
from yuuno2.clips.combined_alpha import AlphaFrame, AlphaClip


class CustomMockFrame(MockFrame):

    def __init__(self, size: Size, format: RawFormat, meta: dict):
        self._size = size
        self.format = format
        self.meta = meta
        self._last_plane = None
        self._last_format = None

    @property
    def size(self) -> Size:
        return self._size

    @property
    def native_format(self) -> RawFormat:
        return self.format

    async def can_render(self, format: RawFormat) -> bool:
        return self.format == format

    async def render_into(self, buffer: Buffer, plane: int, format: RawFormat, offset: int = 0) -> int:
        self._last_plane = plane
        self._last_format = format
        return plane

    async def get_metadata(self) -> Mapping[str, Union[int, str, bytes]]:
        return self.meta


class TestAlphaFrame(AsyncTestCase):

    async def test_attributes(self):
        m = CustomMockFrame(Size(1, 1), RGB24, {'type': 'm', 'a': 0})
        a = CustomMockFrame(Size(1, 2), GRAY8, {'type': 'a', 'b': 1})

        async with m, a:
            async with AlphaFrame(m, a) as f:
                self.assertEqual(f.size, Size(1, 1))
                self.assertEqual(f.native_format, RGB24._replace(num_fields=4))

    async def test_attributes_packed(self):
        mf = RGB24._replace(planar=False)

        m = CustomMockFrame(Size(1, 1), mf, {'type': 'm', 'a': 0})
        a = CustomMockFrame(Size(1, 2), GRAY8, {'type': 'a', 'b': 1})

        async with m, a:
            async with AlphaFrame(m, a) as f:
                self.assertEqual(f.size, Size(1, 1))
                self.assertEqual(f.native_format, mf)


    async def test_metadata(self):
        m = CustomMockFrame(Size(1, 1), RGB24, {'type': 'm', 'a': 0})
        a = CustomMockFrame(Size(1, 2), GRAY8, {'type': 'a', 'b': 1})
        async with AlphaFrame(m, a) as f:
            self.assertDictEqual(await f.get_metadata(), {'type': 'm', 'a': 0, 'b': 1})

    async def test_can_render(self):
        m = CustomMockFrame(Size(1, 1), RGB24, {'type': 'm', 'a': 0})
        a = CustomMockFrame(Size(1, 2), GRAY8, {'type': 'a', 'b': 1})
        async with AlphaFrame(m, a) as f:
            self.assertTrue(await f.can_render(RGBA32))
            self.assertTrue(await f.can_render(RGB24))
            self.assertFalse(await f.can_render(GRAY8))

    async def test_render_into(self):
        m = CustomMockFrame(Size(1, 1), RGB24, {'type': 'm', 'a': 0})
        a = CustomMockFrame(Size(1, 2), GRAY8, {'type': 'a', 'b': 1})
        async with AlphaFrame(m, a) as f:
            self.assertEqual(await f.render_into(bytearray(), 0, RGBA32, 0), 0)
            self.assertEqual(m._last_format, RGB24)
            self.assertEqual(m._last_plane, 0)
            self.assertIsNone(a._last_format)
            self.assertIsNone(a._last_plane)

            self.assertEqual(await f.render_into(bytearray(), 1, RGBA32, 0), 1)
            self.assertIsNone(a._last_format)
            self.assertIsNone(a._last_plane)
            self.assertEqual(m._last_format, RGB24)
            self.assertEqual(m._last_plane, 1)

            self.assertEqual(await f.render_into(bytearray(), 2, RGBA32, 0), 2)
            self.assertIsNone(a._last_format)
            self.assertIsNone(a._last_plane)
            self.assertEqual(m._last_format, RGB24)
            self.assertEqual(m._last_plane, 2)

            m._last_plane = None
            m._last_format = None
            self.assertEqual(await f.render_into(bytearray(), 3, RGBA32, 0), 0)
            self.assertEqual(a._last_format, GRAY8)
            self.assertEqual(a._last_plane, 0)
            self.assertIsNone(m._last_format)
            self.assertIsNone(m._last_plane)

    async def test_resources_owned(self):
        m = CustomMockFrame(Size(1, 1), RGB24, {'type': 'm', 'a': 0})
        a = CustomMockFrame(Size(1, 2), GRAY8, {'type': 'a', 'b': 1})
        f = AlphaFrame(m, a)
        await f.acquire()
        self.assertTrue(m.acquired)
        self.assertTrue(a.acquired)

        await f.release()
        self.assertFalse(m.acquired)
        self.assertFalse(m.acquired)

    async def test_resource_not_owned(self):
        m = CustomMockFrame(Size(1, 1), RGB24, {'type': 'm', 'a': 0})
        a = CustomMockFrame(Size(1, 2), GRAY8, {'type': 'a', 'b': 1})

        async with m, a:
            f = AlphaFrame(m, a)
            await f.acquire()
            self.assertTrue(m.acquired)
            self.assertTrue(a.acquired)

            await f.release()
            self.assertTrue(m.acquired)
            self.assertTrue(m.acquired)


class TestAlphaClip(AsyncTestCase):

    async def test_resource_owned(self):
        m = MockClip()
        a = MockClip()

        f = AlphaClip(m, a)
        await f.acquire()
        self.assertTrue(m.acquired)
        self.assertTrue(a.acquired)

        await f.release()
        self.assertFalse(m.acquired)
        self.assertFalse(a.acquired)

    async def test_resource_not_owned(self):
        m = MockClip()
        a = MockClip()
        f = AlphaClip(m, a)

        async with m, a:
            await f.acquire()
            self.assertTrue(m.acquired)
            self.assertTrue(a.acquired)

            await f.release()
            self.assertTrue(m.acquired)
            self.assertTrue(a.acquired)

