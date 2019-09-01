import asyncio
import os
import sys
from asyncio import ProactorEventLoop, wait_for

from aiounittest import AsyncTestCase

from yuuno2.providers.remote.client import RemoteScript
from yuuno2.providers.single import SingleScriptProvider
from yuuno2.tests.mocks import MockScript
from yuuno2server.subprocesses import SubprocessScript

MOCK_PROVIDER = lambda: SingleScriptProvider(MockScript({"test": f"{os.getppid()}"}))


if os.name == 'posix':
    def pid_exists(pid):
        """Check whether pid exists in the current process table."""
        import errno
        if pid < 0:
            return False
        try:
            os.kill(pid, 0)
        except OSError as e:
            return e.errno == errno.EPERM
        else:
            return True
else:
    def pid_exists(pid):
        import ctypes
        kernel32 = ctypes.windll.kernel32
        SYNCHRONIZE = 0x100000

        process = kernel32.OpenProcess(SYNCHRONIZE, 0, pid)
        if process != 0:
            kernel32.CloseHandle(process)
            return True
        else:
            return False


class TestSubprocessScript(AsyncTestCase):

    if sys.platform.startswith("win"):
        def get_event_loop(self):
            return ProactorEventLoop()

    async def test_make_subprocess(self):
        transport, connection = await SubprocessScript.create_subprocess(
            "yuuno2server.tests.test_subprocess:MOCK_PROVIDER"
        )

        async with connection:
            rs = RemoteScript(connection)
            async with rs:
                self.assertEqual(str(os.getpid()), await wait_for(rs.get_config("test"), 5))

            transport.get_pipe_transport(0).close()
            for i in range(11):
                if transport.is_closing():
                    break
                await asyncio.sleep(1)
            else:
                self.fail("Did not exit in time.")

    async def test_subprocess_script(self):
        subprocess = SubprocessScript("yuuno2server.tests.test_subprocess:MOCK_PROVIDER")
        async with subprocess:
            pid = await wait_for(subprocess.get_config("test"), 5)
            self.assertEqual(str(os.getpid()), pid)

        self.assertFalse(pid_exists(pid))
