from asyncio import wait_for

from aiounittest import AsyncTestCase

from yuuno2.networking.pipe import pipe_bidi
from yuuno2.providers.remote.client import RemoteScript, RemoteScriptProvider
from yuuno2.providers.remote.server import RemoteScriptServer, RemoteScriptProviderServer
from yuuno2.providers.single import SingleScriptProvider
from yuuno2.tests.mocks import MockScript
from yuuno2.tests.utils import timeout_context


class TestRemoteScript(AsyncTestCase):

    async def test_remote_script_config(self):
        c_client, c_server = pipe_bidi()

        rs = MockScript({
            "test-int": 1,
            "test-bytes": b"abc",
            "test-null": None,
            "test-string": "foo",
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
            self.assertEqual( await wait_for(rsc.get_config("test-string"), 10), "foo")
            with self.assertRaises(KeyError):
                await wait_for(rsc.get_config("test-unset"), 10)
            self.assertIs(await wait_for(rsc.get_config("test-unset", unset), 10), unset)

            for val in [2, b"def", None, 6.2831852, "bar"]:
                await wait_for(rsc.set_config("test-set", val), 10)
                self.assertEqual(
                    await wait_for(rsc.list_config(), 10),
                    ["test-int", "test-bytes", "test-null", "test-string", "test-float", "test-set"]
                )
                self.assertEqual(await wait_for(rsc.get_config("test-set"), 10), val)

    async def test_remote_script_run(self):
        c_client, c_server = pipe_bidi()

        rs = MockScript({})
        rss = RemoteScriptServer(rs, c_server)
        rsc = RemoteScript(c_client)

        async with timeout_context(rss, 10), timeout_context(rsc, 10):
            await wait_for(rsc.run("test-code-string"), 10)
            self.assertEqual(await wait_for(rsc.get_config("last-command"), 10), "test-code-string")

            await wait_for(rsc.run(b"test-code-binary"), 10)
            self.assertEqual(await wait_for(rsc.get_config("last-command"), 10), b"test-code-binary")

    async def test_remote_clip_map(self):
        c_client, c_server = pipe_bidi()

        rs = MockScript({})
        rss = RemoteScriptServer(rs, c_server)
        rsc = RemoteScript(c_client)

        async with timeout_context(rss, 10), timeout_context(rsc, 10):
            clips = await wait_for(rsc.retrieve_clips(), 10)
            self.assertEqual(len(clips), 1)
            self.assertEqual(list(clips), ["test"])

    async def test_remote_clip_access(self):
        c_client, c_server = pipe_bidi()

        rs = MockScript({})
        rss = RemoteScriptServer(rs, c_server)
        rsc = RemoteScript(c_client)

        async with timeout_context(rss, 10), timeout_context(rsc, 10):
            clips = await wait_for(rsc.retrieve_clips(), 10)

            async with clips["test"] as c:
                self.assertEqual(len(c), 1)


class TestRemoteScriptProvider(AsyncTestCase):
    async def test_get_script(self):
        c_client, c_server = pipe_bidi()

        ms = MockScript({"id": id(self)})
        sp = SingleScriptProvider(ms)

        rsps = RemoteScriptProviderServer(sp, c_server)
        rspc = RemoteScriptProvider(c_client)

        async with timeout_context(rsps, 10), timeout_context(rspc, 10):
            rsc = await rspc.get()
            async with timeout_context(rsc, 10):
                self.assertEqual(await wait_for(rsc.get_config("id"), 10), id(self))
