from abc import ABC, abstractmethod
from typing import NoReturn, Mapping, Type, Tuple, Callable, Dict, List

from yuuno2.networking.base import Connection
from yuuno2.networking.multiplex import Multiplexer, Channel
from yuuno2.networking.reqresp import ReqRespClient, ReqRespServer
from yuuno2.resource_manager import Resource, register
from yuuno2.typings import ConfigTypes


ConverterTypeSend = Callable[[ConfigTypes], Tuple[ConfigTypes, List[bytes]]]
ConverterTypeRecv = Callable[[ConfigTypes, List[bytes]], ConfigTypes]
NoneType = type(None)


IDENTITY_SEND: ConverterTypeSend = lambda x:    (x,    [])
IDENTITY_RECV: ConverterTypeRecv = lambda d, b: d
BYTES_SEND:    ConverterTypeSend = lambda x:    (None, [x])
BYTES_RECV:    ConverterTypeRecv = lambda d, b: b[0]


TYPE_MAP_SEND: Dict[Type[ConfigTypes], Tuple[str, ConverterTypeSend]] = {
    bytes:    ("bytes",  BYTES_SEND),
    str:      ("string", IDENTITY_SEND),
    int:      ("int",    IDENTITY_SEND),
    float:    ("float",  IDENTITY_SEND),
    NoneType: ("null",   IDENTITY_SEND),
}
TYPE_MAP_RECV: Dict[str, ConverterTypeRecv] = {
    "bytes":  BYTES_RECV,
    "string": IDENTITY_RECV,
    "int":    IDENTITY_RECV,
    "float":  IDENTITY_RECV,
    "null":   IDENTITY_RECV,
}


class Multiplexed(Resource, ABC):
    def __init__(self, connection: Connection):
        super().__init__()
        self.connection = connection
        self._multiplexer = None
        self._channel = None
        self._control = None

    @abstractmethod
    def create_endpoint(self, connection: Connection) -> Resource:
        pass

    async def _acquire(self) -> NoReturn:
        await self.connection.acquire()
        register(self.connection, self)

        self._multiplexer = Multiplexer(self.connection)

        await self._multiplexer.acquire()
        register(self, self._multiplexer)
        self._channel = self._multiplexer.connect("control")
        await self._channel.acquire()

        self._control = self.create_endpoint(self._channel)
        register(self, self._control)
        await self._control.acquire()

    async def _release(self) -> NoReturn:
        await self.connection.release(force=False)


class MultiplexedClient(Multiplexed):

    def __init__(self, connection: Connection):
        super().__init__(connection)
        self._client = None

    def create_endpoint(self, connection: Connection) -> Resource:
        self._client = self.create_client(connection)
        return self._client

    @abstractmethod
    def create_client(self, connection: Connection) -> ReqRespClient:
        pass


class MultiplexedServer(Multiplexed):

    def __init__(self, connection: Connection):
        super().__init__(connection)
        self._server = None

    def create_endpoint(self, connection: Connection) -> Resource:
        self._server = self.create_server(connection)
        return self._server

    @abstractmethod
    def create_server(self, connection: Connection) -> ReqRespServer:
        self._server = self.create_server(self._channel)
        return self._server
