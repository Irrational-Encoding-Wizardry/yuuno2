import json
from typing import NamedTuple, Union, Sequence, Optional, NoReturn

from yuuno2.networking.base import Message, MessageInputStream, MessageOutputStream, Connection
from yuuno2.networking.pipe import pipe
from yuuno2.networking.serializer import ByteOutputStream, bytes_protocol
from yuuno2.resource_manager import Resource, register


class WebsocketMessage(NamedTuple):
    chunk: Union[dict, bytes]


    @classmethod
    def from_message(cls, message: Message) -> 'WebsocketMessage':
        if len(message.blobs):
            chunk = ByteOutputStream.write_message(message)
        else:
            chunk = message.values

        return cls(chunk)

    @classmethod
    def from_socket(cls, data: Union[str, dict, bytes]) -> 'WebsocketMessage':
        if isinstance(data, bytes):
            return cls(data)

        if isinstance(data, str):
            data = json.loads(data)

        return cls(data)

    def to_message(self) -> Sequence[Message]:
        if not self.is_text():
            proto = bytes_protocol()
            yield from proto.feed(self.chunk)
            return

        yield Message(self.chunk, [])

    def is_text(self) -> bool:
        return isinstance(self.chunk, dict)

    def to_ws_json(self) -> Optional[dict]:
        if not self.is_text():
            return None
        return self.chunk

    def to_ws_string(self) -> Optional[str]:
        if not self.is_text():
            return None
        return json.dumps(self.chunk)

    def to_ws_bytes(self) -> Optional[bytes]:
        if self.is_text():
            return None
        return self.chunk


class WebsocketHandler(Resource):

    def __init__(self):
        self._p_in, self._p_out = pipe()
        self.closing = False

    async def send(self, message: Message):
        await self.check_acquired()
        serialized = WebsocketMessage.from_message(message)
        await self.on_send(serialized)

    async def on_send(self, message: WebsocketMessage):
        """
        Override this to send a websocket message to the other side.
        """
        pass

    async def deliver(self, message: WebsocketMessage):
        """
        Call this with a websocket message to deliver it to the yuuno application.
        """
        await self.check_acquired()

        for msg in message.to_message():
            await self._p_out.write(msg)

    async def on_close(self):
        """
        Override this to implement closing of the websocket.
        """
        pass

    async def close(self):
        if not self.closing:
            self.closing = True
            await self.on_close()

    async def _acquire(self) -> NoReturn:
        await self._p_out.acquire()
        await self._p_in.acquire()
        register(self, self._p_in)
        register(self, self._p_out)

    async def _release(self) -> NoReturn:
        await self.close()

    def make_connection(self) -> Connection:
        """
        Creates a connection that can be used by other parts of Yuuno.
        """
        return Connection(WebsocketInputStream(self), WebsocketOutputStream(self))


class WebsocketInputStream(MessageInputStream):

    def __init__(self, handler: WebsocketHandler):
        self.handler = handler

    async def read(self) -> Optional[Message]:
        await self.check_acquired()
        await self.handler._p_in.read()

    async def _acquire(self) -> NoReturn:
        register(self.handler, self)
        register(self.handler._p_in, self)

    async def _release(self) -> NoReturn:
        pass


class WebsocketOutputStream(MessageOutputStream):

    def __init__(self, handler: WebsocketHandler):
        self.handler = handler

    async def write(self, message: Message) -> NoReturn:
        await self.check_acquired()
        await self.handler.send(message)

    async def close(self) -> NoReturn:
        await self.check_acquired()
        await self.handler.close()

    async def _acquire(self) -> NoReturn:
        register(self.handler, self)

    async def _release(self) -> NoReturn:
        pass

