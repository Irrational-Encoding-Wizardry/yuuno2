import json
from typing import Union, Optional

from tornado.websocket import WebSocketHandler

from yuuno2.networking.base import Message, MessageOutputStream, Connection
from yuuno2.networking.pipe import pipe
from yuuno2.networking.serializer import bytes_protocol, ByteOutputStream
from yuuno2.networking.websocket import WebsocketHandler, WebsocketMessage
from yuuno2.resource_manager import NonAbcResource, register
from yuuno2.script import ScriptProvider


class TornadoSocketHandler(WebsocketHandler):
    """
    Yuuno interop part.
    """

    def __init__(self, ch: 'ConnectionHandler'):
        super().__init__()
        self.ch = ch

    async def on_send(self, message: WebsocketMessage):
        if message.is_text():
            await self.ch.write_message(message.to_ws_json(), binary=False)
        else:
            await self.ch.write_message(message.to_ws_bytes(), binary=True)

    async def on_close(self):
        self.ch.close()


class ConnectionHandler(WebSocketHandler, NonAbcResource):
    """
    Tornado interop part.
    """

    def __init__(self, manager: ScriptProvider, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager = manager
        self.ws_handler = TornadoSocketHandler(self)

    async def prepare(self) -> None:
        await self.acquire()
        await self.ws_handler.acquire()

        register(self.manager, self)
        register(self, self.ws_handler)

    async def open(self):
        await self.on_established(self.ws_handler.make_connection())

    async def on_established(self, connection: Connection):
        self.write_message()

    async def on_close(self) -> None:
        if not self._closing:
            self._closing = True
            await self.release(force=True)

    async def on_message(self, message: Union[str, bytes]) -> None:
        await self.ws_handler.deliver(WebsocketMessage.from_socket(message))

    async def _acquire(self):
        pass

    async def _release(self):
        self._closing = True
        self.close()

