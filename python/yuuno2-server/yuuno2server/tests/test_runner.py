import os
import tempfile
from contextlib import contextmanager
from asyncio import wait_for
from yuuno2.tests.mocks import MockScript

from aiounittest import AsyncTestCase

from yuuno2server.runner import LocalScript


@contextmanager
def retain_cd_after():
    cd = os.getcwd()
    try:
        yield cd
    finally:
        os.chdir(cd)


class TestLocalScript(AsyncTestCase):

    async def test_ro_pid(self):
        ms = MockScript()
        async with ms:
            ls = LocalScript(ms)
            async with ls:
                self.assertEqual(os.getpid(), await wait_for(ls.get_config("subprocess.pid"), 5))

                await wait_for(ls.set_config("subprocess.pid", 123), 5)
                self.assertEqual(os.getpid(), await wait_for(ls.get_config("subprocess.pid"), 5))

    async def test_env(self):
        ms = MockScript()
        async with ms:
            ls = LocalScript(ms)
            async with ls:
                raw_env = os.environ.keys()
                env = ["subprocess.env." + k for k in raw_env]
                values = [f for f in (await wait_for(ls.list_config(), 5)) if f.startswith("subprocess.env.")]
                self.assertEqual(env, values)

                os.environ["test"] = "abc"
                self.assertEqual("abc", await wait_for(ls.get_config("subprocess.env.test"), 5))
                await wait_for(ls.set_config("subprocess.env.test", "def"), 5)
                self.assertEqual(os.environ["test"], "def")
                await wait_for(ls.set_config("subprocess.env.test", None), 5)
                self.assertNotIn("test", os.environ)

    async def test_cd(self):
        ms = MockScript()
        async with ms:
            ls = LocalScript(ms)
            async with ls:
                with retain_cd_after() as cd:
                    self.assertEqual(cd, await wait_for(ls.get_config("subprocess.cd"), 5))
                    d = tempfile.mkdtemp()
                    await wait_for(ls.set_config("subprocess.cd", str(d)), 5)
                    self.assertEqual(os.getcwd(), d)

    async def test_pass_config_down(self):
        ms = MockScript({"test": str(id(self))})
        async with ms:
            ls = LocalScript(ms)
            async with ls:
                self.assertEqual(str(id(self)), await wait_for(ls.get_config("test"), 5))
