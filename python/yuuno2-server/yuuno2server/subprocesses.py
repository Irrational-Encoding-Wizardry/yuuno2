import asyncio
import os
import sys
from typing import Optional, None, Mapping, Union, Any, Sequence
from asyncio import SubprocessProtocol, SubprocessTransport, AbstractEventLoop, get_running_loop

from yuuno2.clip import Clip
from yuuno2.networking.asyncio import YuunoBaseProtocol, ConnectionOutputStream, ConnectionInputStream
from yuuno2.networking.base import Connection
from yuuno2.providers.remote.client import RemoteScript
from yuuno2.resource_manager import register
from yuuno2.script import Script, NOT_GIVEN
from yuuno2.typings import ConfigTypes


class SubprocessConnection(SubprocessProtocol, YuunoBaseProtocol):
    """
    This is a simple subprocess connection.
    """
    transport: SubprocessTransport

    def __init__(self):
        self._finishing = False
        super().__init__()

    def connection_made(self, transport: SubprocessTransport):
        """Called when a connection is made.

        The argument is the transport representing the pipe connection.
        To receive data, wait for data_received() calls.
        When the connection is closed, connection_lost() is called.
        """
        self.transport = transport
        self.continue_writing()

    def connection_lost(self, exc):
        """Called when the connection is lost or closed.

        The argument is an exception object or None (the latter
        meaning a regular EOF is received or the connection was
        aborted or closed).
        """
        self.finishing()

    def pause_writing(self):
        """Called when the transport's buffer goes over the high-water mark.

        Pause and resume calls are paired -- pause_writing() is called
        once when the buffer goes strictly over the high-water mark
        (even if subsequent writes increases the buffer size even
        more), and eventually resume_writing() is called once when the
        buffer size reaches the low-water mark.

        Note that if the buffer size equals the high-water mark,
        pause_writing() is not called -- it must go strictly over.
        Conversely, resume_writing() is called when the buffer size is
        equal or lower than the low-water mark.  These end conditions
        are important to ensure that things go as expected when either
        mark is zero.

        NOTE: This is the only Protocol callback that is not called
        through EventLoop.call_soon() -- if it were, it would have no
        effect when it's most needed (when the app keeps writing
        without yielding until pause_writing() is called).
        """
        self.stop_writing()

    def resume_writing(self):
        """Called when the transport's buffer drains below the low-water mark.

        See pause_writing() for details.
        """
        self.continue_writing()

    def pipe_data_received(self, fd, data):
        """Called when the subprocess writes data into stdout/stderr pipe.

        fd is int file descriptor.
        data is bytes object.
        """
        if fd == 1:
            self.feed(data)
        else:
            fp = sys.stderr
            if hasattr(fp, "buffer"):
                fp = fp.buffer
            else:
                data = data.decode("utf-8")
            fp.write(data)
            fp.flush()

    def pipe_connection_lost(self, fd, exc):
        """Called when a file descriptor associated with the child process is
        closed.

        fd is the int file descriptor that was closed.
        """
        self.finishing()

    def process_exited(self):
        """Called when subprocess has exited."""
        self.finishing()

    def finishing(self):
        if not self._finishing:
            self._finishing = True
            super().finishing()

    def feed(self, data: Optional[bytes]):
        if not super().feed(data):
            pt = self.transport.get_pipe_transport(1)
            if hasattr(pt, "pause_reading"):
                pt.pause_reading()

    def after_message_read(self):
        pt = self.transport.get_pipe_transport(1)
        if hasattr(pt, "resume_reading"):
            pt.resume_reading()

    def write_message_data(self, data: bytes):
        self.transport.get_pipe_transport(0).write(data)


class SubprocessScript(Script):

    def __init__(self, provider: str, event_loop: str = "default", *, loop: AbstractEventLoop=None):
        if loop is None:
            loop = get_running_loop()
        self.loop = loop

        self.provider = provider
        self.event_loop = event_loop
        self._script: Optional[RemoteScript] = None

    def activate(self) -> None:
        pass

    def deactivate(self) -> None:
        pass

    async def set_config(self, key: str, value: ConfigTypes) -> None:
        await self.ensure_acquired()
        await self._script.set_config(key, value)

    async def get_config(self, key: str, default: Union[object, ConfigTypes] = NOT_GIVEN) -> ConfigTypes:
        await self.ensure_acquired()
        return await self._script.get_config(key, default)

    async def list_config(self) -> Sequence[str]:
        await self.ensure_acquired()
        return await self._script.list_config()

    async def run(self, code: Union[bytes, str]) -> Any:
        await self.ensure_acquired()
        return await self._script.run(code)

    async def retrieve_clips(self) -> Mapping[str, Clip]:
        await self.ensure_acquired()
        return await self._script.retrieve_clips()

    async def _acquire(self) -> None:
        self._transport, self._connection = await self.create_subprocess(self.provider, self.event_loop, loop=self.loop)
        await self._connection.acquire()
        register(self._connection, self)
        self._script = RemoteScript(self._connection)

        await self._script.acquire()
        register(self._script, self)

    async def _release(self) -> None:
        self._transport.get_pipe_transport(0).close()
        while not self._transport.is_closing():
            await asyncio.sleep(0.1)

        await self._script.release(force=True)
        await self._connection.release(force=True)
        self._transport.close()

    @staticmethod
    async def create_subprocess(provider: str, event_loop: str="default", *, loop=None):
        if loop is None:
            loop = get_running_loop()

        path = os.path.join(os.path.dirname(__file__), "runner.py")
        call = [sys.executable, path, "--provider", provider, "--event-loop", event_loop]

        yuuno_protocol: SubprocessConnection

        transport, yuuno_protocol = await loop.subprocess_exec(SubprocessConnection, *call)
        return transport, Connection(
            ConnectionInputStream(yuuno_protocol),
            ConnectionOutputStream(yuuno_protocol)
        )
