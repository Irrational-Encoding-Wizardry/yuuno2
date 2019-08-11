from typing import Sequence, Optional, List, Any, Dict

from yuuno2.clips.remote import ClipServer
from yuuno2.networking.base import Connection, Message
from yuuno2.networking.multiplex import Multiplexer
from yuuno2.networking.reqresp import ReqRespServer
from yuuno2.providers.remote.helpers import TYPE_MAP_RECV, ConverterTypeRecv, TYPE_MAP_SEND, MultiplexedServer
from yuuno2.resource_manager import register, Resource
from yuuno2.script import Script, ScriptProvider
from yuuno2.typings import ConfigTypes


NOT_SET = object()


class _RemoteScriptServer(ReqRespServer):

    def __init__(self, script: Script, connection: Connection, multiplexer: Multiplexer):
        super().__init__(connection)
        self.script = script
        self.multiplexer = multiplexer
        self.connections = {}

    async def on_set_config(self, key: str, value: ConfigTypes, type: str, _buffers: List[bytes]):
        converter: ConverterTypeRecv = TYPE_MAP_RECV[type]
        value = converter(value, _buffers)
        await self.script.set_config(key, value)
        return Message({}, [])

    async def on_get_config(self, key: str):
        result = await self.script.get_config(key, NOT_SET)
        if result is NOT_SET:
            return Message({"type": "unset", "value": None}, [])

        vtype, converter = TYPE_MAP_SEND[type(result)]
        value, buffers = converter(result)

        return Message({"type": vtype, "value": value}, buffers)

    async def on_list_config(self):
        keys = await self.script.list_config()
        return Message({"keys": list(keys)}, [])

    async def on_run(self, encoding: Optional[str] = None, _buffers: Sequence[bytes] = (b"",)):
        code = _buffers[0]
        if encoding is not None:
            code = code.decode(encoding)

        await self.script.run(code)
        return Message({}, [])

    async def on_list_clips(self):
        clips = list((await self.script.retrieve_clips()).keys())
        return Message({'clips': clips}, [])

    async def on_register_clip(self, channel_name: str, name: str):
        conn = self.multiplexer.connect(channel_name)
        register(self, conn)
        await conn.acquire()

        clips = await self.script.retrieve_clips()
        clip = clips[name]

        server = ClipServer(clip, conn)
        register(conn, server)
        await server.acquire()

        self.connections[channel_name] = conn
        return Message({}, [])

    async def on_unregister_clip(self, channel_name: str):
        await self.connections[channel_name].release()
        return Message({}, [])


class RemoteScriptServer(MultiplexedServer):

    def __init__(self, script: Script, connection: Connection):
        super().__init__(connection)
        self.script = script

    async def create_server(self, connection: Connection) -> Resource:
        return _RemoteScriptServer(self.script, connection, self._multiplexer)


class _RemoteScriptProviderServer(ReqRespServer):
    def __init__(self, provider: ScriptProvider, connection: Connection, multiplexer: Multiplexer):
        super().__init__(connection)
        self.provider = provider
        self.multiplexer = multiplexer
        self.connections = {}

    async def on_create_script(self, channel_name: str, params: Dict[str, Any]):
        conn = self.multiplexer.connect(channel_name)
        register(self, conn)
        await conn.acquire()

        script = await self.provider.get(**params)

        server = RemoteScriptServer(script, conn)
        register(conn, server)
        await server.acquire()

        self.connections[channel_name] = conn
        return Message({}, [])

    async def on_release_script(self, channel_name: str):
        await self.connections[channel_name].release()
        return Message({}, [])


class RemoteScriptProviderServer(MultiplexedServer):

    def __init__(self, provider: ScriptProvider, connection: Connection):
        super().__init__(connection)
        self.provider = provider

    async def create_server(self, connection: Connection) -> Resource:
        return _RemoteScriptProviderServer(self.provider, connection, self._multiplexer)
