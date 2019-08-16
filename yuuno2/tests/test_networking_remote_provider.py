from asyncio import wait_for
from unittest import skip

from aiounittest import AsyncTestCase
from async_timeout import timeout

from yuuno2.networking.pipe import pipe_bidi
from yuuno2.providers.remote.client import RemoteScriptProvider, RemoteScript
from yuuno2.providers.remote.server import RemoteScriptProviderServer, RemoteScriptServer
from yuuno2.tests.mocks import MockScriptProvider, MockScript
from yuuno2.tests.utils import timeout_context


class TestRemoteScript(AsyncTestCase):

    async def test_remote_script_config(self):
        c_client, c_server = pipe_bidi()

        rs = MockScript({
            "test-int": 1,
            "test-bytes": b"abc",
            "test-null": None,
            "test-string": "test",
            "test-float": 3.1415926
        })
        unset = object()

        rss = RemoteScriptServer(rs, c_server)
        rsc = RemoteScript(c_client)

        async with timeout_context(rss, 10), timeout_context(rsc, 10):
            self.assertEqual(
                await wait_for(rsc.list_config(), 10),
                ["test-int", "test-bytes", "test-null", "test-string", "test-float"]
            )
            self.assertEqual( await wait_for(rsc.get_config("test-int"),    10), 1)
            self.assertEqual( await wait_for(rsc.get_config("test-bytes"),  10), b"abc")
            self.assertIsNone(await wait_for(rsc.get_config("test-null"),   10))
            self.assertEqual( await wait_for(rsc.get_config("test-float"),  10), 3.1415926)
            with self.assertRaises(KeyError):
                await wait_for(rsc.get_config("test-unset"), 10)
            self.assertIs(await wait_for(rsc.get_config("test-unset", unset), 10), unset)


class TestRemoteServer(AsyncTestCase):

    @skip
    async def test_remote_provider(self):
        c_client, c_server = pipe_bidi()

        rsp = RemoteScriptProvider(c_client)

        sp = MockScriptProvider()
        rsps = RemoteScriptProviderServer(sp, c_server)