from asyncio import Lock, Event, gather
from typing import Optional, MutableMapping, NoReturn

from yuuno2.resource_manager import register, Resource

from yuuno2.networking.base import Connection, Message, MessageOutputStream, ConnectionInputStream, \
    ConnectionOutputStream
from yuuno2.networking.reader import ReaderTask
from yuuno2.networking.pipe import PipeOutputStream, PipeInputStream, pipe


class ChannelOutputStream(MessageOutputStream):

    def __init__(self, channel: 'Channel'):
        self.channel = channel
        register(self.channel, self)

    async def write(self, message: Message) -> NoReturn:
        await self.channel.multiplexer.write(
            Message({'target': self.channel.name, 'type': 'message', 'payload': message.values}, message.blobs)
        )

    async def close(self) -> NoReturn:
        self.channel.multiplexer.streams.pop(self.channel.name, None)
        if self.channel.ingress is not None and self.channel.ingress.output is not None:
            await self.channel.ingress.close()

        if self.channel.multiplexer.acquired:
            await self.channel.multiplexer.write(Message({'target': self.channel.name, 'type': 'close'}))

    async def _acquire(self) -> NoReturn:
        pass

    async def _release(self) -> NoReturn:
        await self.close()


class Channel(Connection):

    def __init__(self, multiplexer: 'Multiplexer', name: str):
        self._closed = False

        self.name = name
        self.multiplexer = multiplexer

        self.ingress: Optional[Connection] = None
        self.egress: Optional[ChannelOutputStream] = None
        self._connection_cache = None
        super().__init__(None, None)

        self.input = ConnectionInputStream(self)
        self.output = ConnectionOutputStream(self)

    async def deliver(self, message: Optional[Message]) -> NoReturn:
        if message is None:
            self._closed = True
            if not self.acquired:
                return

        await self.ensure_acquired()
        await self.ingress.write(message)

    async def _acquire(self) -> NoReturn:
        if self.name in self.multiplexer.streams:
            raise RuntimeError("Stream already registered.")

        self.multiplexer.streams[self.name] = self

        self.ingress: Connection = Connection(*pipe())
        await self.ingress.acquire()
        register(self, self.ingress)

        self.egress: ChannelOutputStream = ChannelOutputStream(self)
        await self.egress.acquire()
        register(self, self.egress)

        await gather(self.input.acquire(), self.output.acquire())

    async def _release(self) -> NoReturn:
        await gather(self.input.release(), self.output.release())

        if not self._closed and self.multiplexer.acquired:
            await self.multiplexer.write(Message({
                "target": self.name, "type": "close"
            }))
        self._closed = True

        self.multiplexer.streams.pop(self.name, None)

        await self.ingress.release(force=False)
        await self.egress.release(force=False)
        self.ingress = None
        self.egress = None
        self.multiplexer = None
        self._connection_cache = None

    def _ensure_open(self):
        if self._closed:
            raise ConnectionResetError

    async def read(self) -> Optional[Message]:
        self._ensure_open()
        return (await self.ingress.input.read())

    async def write(self, message: Message):
        self._ensure_open()
        return (await self.egress.write(message))

    async def close(self):
        if not self._closed:
            await self.egress.close()
        self._closed = True

    @property
    def closed(self):
        return self._closed


class Multiplexer(Resource):

    def __init__(self, parent: Connection):
        self.streams: MutableMapping[str, Channel] = {}
        self._w_lock = Lock()
        self._closed = Event()
        self._shutdown = Event()
        self.parent = parent

    async def _delivered(self, raw: Optional[Message]) -> None:
        if not self.acquired:
            return

        if raw is None:
            self._shutdown.set()
            return

        msg, buffers = raw

        connection = msg.get("target", "")
        type = msg.get("type", "message")

        if type in ("close", "illegal"):
            reader = self.streams.pop(connection, None)
            if reader is None:
                return
            await reader.deliver(None)
            return

        if connection not in self.streams:
            await self.write(Message({"target": connection, "type": "close", "payload": {}}))
            return

        if "payload" not in msg:
            await self.write(Message({"target": connection, "type": "illegal", "payload": {}}))
            return

        await self.streams[connection].deliver(Message(msg["payload"], buffers))
        return

    def connect(self, name: str) -> Channel:
        c = Channel(self, name)
        register(self, c)
        return c

    async def write(self, message: Message):
        await self.ensure_acquired()
        async with self._w_lock:
            await self.parent.write(message)

    async def close(self):
        await self.ensure_acquired()
        async with self._w_lock:
            await self.parent.close()
            self._closed.set()

    async def _acquire(self):
        await self.parent.acquire()
        _task = ReaderTask(self.parent.input, self._delivered)

        register(self, _task)
        await _task.acquire()

        register(self.parent, self)

    async def _release(self):
        await self.parent.release(force=False)
