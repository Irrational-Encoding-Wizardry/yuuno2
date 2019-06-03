from aiounittest import AsyncTestCase
from yuuno2.tests.mocks import MockScript
from yuuno2.providers.single import SingleScriptProvider


class TestSingleScript(AsyncTestCase):

    async def test_non_owned(self):
        script = MockScript()
        single = SingleScriptProvider(script)
        async with script:
            async with single:
                pass
            self.assertTrue(script.acquired)

    async def test_owner(self):
        script = MockScript()
        single = SingleScriptProvider(script)
        async with single:
            self.assertTrue(script.acquired)
        self.assertFalse(script.acquired)

    async def test_always_same(self):
        script = MockScript()
        single = SingleScriptProvider(script)
        async with single:
            self.assertIs(script, await single.get())
            self.assertIs(script, await single.get())
