from aiounittest import AsyncTestCase
from yuuno2.providers.named import NamedScriptProvider
from yuuno2.tests.mocks import MockScriptProvider


class TestNamedScriptProvider(AsyncTestCase):

    async def test_unknown_script(self):
        sp = MockScriptProvider()
        named = NamedScriptProvider(sp)
        async with sp, named:
            self.assertIsNone(await named.get(name="unknown"))

    async def test_anonymous_script(self):
        sp = MockScriptProvider()
        named = NamedScriptProvider(sp)
        async with sp, named:
            self.assertIsNotNone(await named.get())

    async def test_create_script(self):
        sp = MockScriptProvider()
        named = NamedScriptProvider(sp)
        async with sp, named:
            script = await named.get(name="named", create=True)
            self.assertIsNotNone(script)
            self.assertIs(script, await named.get(name="named"))

    async def test_destroy_script(self):
        sp = MockScriptProvider()
        named = NamedScriptProvider(sp)
        async with sp, named:
            script = await named.get(name="named", create=True)
            await script.acquire()
            await script.release()
            self.assertIsNone(await named.get(name="named"))

    async def test_destroy_children(self):
        sp = MockScriptProvider()
        named = NamedScriptProvider(sp)
        async with sp, named:
            script = await named.get(name="named", create=True)
            await script.acquire()
        self.assertFalse(script.acquired)