import asyncio
from asyncio import get_running_loop
from typing import NoReturn, Optional, Union, Sequence

from IPython import get_ipython
from ipykernel.comm import Comm, CommManager
from ipykernel.ipkernel import Kernel

from yuuno2.providers.remote.server import RemoteScriptServer
from yuuno2.providers.wrapper import WrappedScript
from yuuno2.resource_manager import register, Resource
from yuuno2.networking.base import MessageInputStream, Message, Connection
from yuuno2.networking.base import MessageOutputStream
from yuuno2.networking.pipe import pipe
from yuuno2.script import Script, NOT_GIVEN
from yuuno2.typings import ConfigTypes


class CommConnection(Connection):

    def __init__(self, comm: Comm):
        super().__init__(CommInputStream(comm), CommOutputStream(comm))


class CommInputStream(MessageInputStream):

    def __init__(self, comm: Comm):
        self._pipe_r, self._pipe_w = pipe()
        self.comm = comm
        self._on_close = lambda: None

    async def _deliver(self, msg: dict):
        content = msg["content"]
        data = content["data"]
        buffers = msg.get("_buffers", [])
        await self._pipe_w.write(Message(data, buffers))

    async def _close(self, _: dict):
        await self._pipe_w.close()
        self._call_close_cb()

    def _call_close_cb(self):
        self._on_close()
        self._on_close = lambda: None

    async def _acquire(self) -> NoReturn:
        await self._pipe_r.acquire()
        await self._pipe_w.acquire()
        register(self, self._pipe_r)
        register(self, self._pipe_w)

        loop = get_running_loop()
        self.comm.on_msg(lambda msg: asyncio.run_coroutine_threadsafe(self._deliver(msg), loop))
        self.comm.on_close(lambda msg: asyncio.run_coroutine_threadsafe(self._close(msg), loop))

    async def _release(self) -> NoReturn:
        self.comm.on_msg(None)
        self.comm.on_close(None)

    async def read(self) -> Optional[Message]:
        await self.ensure_acquired()
        return await self._pipe_r.read()


class CommOutputStream(MessageOutputStream):

    def __init__(self, comm: Comm):
        self.comm = comm

    async def write(self, message: Message) -> NoReturn:
        await self.ensure_acquired()
        self.comm.send(message.values, buffers=message.blobs)

    async def close(self) -> NoReturn:
        await self.ensure_acquired()
        self.comm.close()

    async def _acquire(self) -> NoReturn:
        pass

    async def _release(self) -> NoReturn:
        pass


class JupyterForwardedScript(WrappedScript):

    def __init__(self, comm: Comm, script: Script):
        super().__init__(script)
        self.comm = comm

    async def get_config(self, key: str, default: Union[object, ConfigTypes] = NOT_GIVEN) -> ConfigTypes:
        if key.startswith("notebook."):
            actual_key = key[9:]
            if actual_key == "comm.id":
                return self.comm.comm_id

        return await super().get_config(key, default)

    async def set_config(self, key: str, value: ConfigTypes) -> NoReturn:
        if key.startswith("notebook."):
            actual_key = key[9:]
            if actual_key == "comm.id":
                return
        return await super().set_config(key, value)

    async def list_config(self) -> Sequence[str]:
        return [
            *(await super().list_config()),
            "notebook.comm.id"
        ]


class JupyterCommManager(Resource):

    def __init__(self, script: Script):
        self.script = script
        register(self.script, self)

        self.connections = {}
        self.loop = None

    async def _accept_comm(self, comm: Comm, msg):
        connection = CommConnection(comm)
        await connection.acquire()

        server = RemoteScriptServer(self.script, connection)
        await server.acquire()
        register(self, server)

        self.connections[comm.comm_id] = server

        async def _on_close():
            await server.release(force=True)
            self.connections.pop(comm.comm_id)

        connection.input.on_close = lambda: asyncio.run_coroutine_threadsafe(_on_close(), self.loop)

    _accept_comm_sync = lambda self, comm, msg: asyncio.run_coroutine_threadsafe(self._accept_comm(comm, msg), self.loop)

    async def _acquire(self) -> NoReturn:
        shell = get_ipython()
        self.loop = get_running_loop()
        mgr: CommManager = shell.kernel.comm_manager
        mgr.register_target("yuuno2", self._accept_comm_sync)

    async def _release(self) -> NoReturn:
        shell = get_ipython()
        mgr: CommManager = shell.kernel.comm_manager
        mgr.unregister_target("yuuno2", self._accept_comm_sync)
        for comm in list(self.connections.values()):
            await comm.release()


