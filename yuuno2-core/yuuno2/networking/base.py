from abc import ABC, abstractmethod
from asyncio import gather
from typing import NamedTuple, List, Mapping, Union, Optional, NoReturn

from yuuno2.resource_manager import Resource, register

AnyJSON = Union[str, int, float, bool, None, Mapping[str, 'AnyJSON'], List['AnyJSON']]
JSON = Mapping[str, AnyJSON]


class Message(NamedTuple):
    values: JSON
    blobs: List[bytes] = []


class MessageInputStream(Resource, ABC):

    @abstractmethod
    async def read(self) -> Optional[Message]:
        pass


class MessageOutputStream(Resource, ABC):

    @abstractmethod
    async def write(self, message: Message) -> NoReturn:
        pass

    @abstractmethod
    async def close(self) -> NoReturn:
        pass


class Connection(Resource):
    input: MessageInputStream
    output: MessageOutputStream

    def __init__(self, input: MessageInputStream, output: MessageOutputStream):
        self.input = input
        self.output = output

    async def _acquire(self):
        await gather(self.input.acquire(), self.output.acquire())
        register(self.input, self)
        register(self.output, self)


    async def _release(self):
        await gather(
            self.input.release(force=False),
            self.output.release(force=False)
        )
        self.input = None
        self.output = None

    async def close(self):
        await self.ensure_acquired()
        await self.output.close()

    async def write(self, message: Message):
        await self.ensure_acquired()
        await self.output.write(message)

    async def read(self) -> Optional[Message]:
        await self.ensure_acquired()
        return (await self.input.read())


class ConnectionOutputStream(MessageOutputStream):

    def __init__(self, connection: Connection):
        self.connection = connection

    async def write(self, message: Message) -> NoReturn:
        return await self.connection.write(message)

    async def close(self) -> NoReturn:
        return await self.connection.close()

    async def _acquire(self) -> NoReturn:
        await self.connection.acquire()
        register(self.connection, self)

    async def _release(self) -> NoReturn:
        await self.connection.release(force=False)


class ConnectionInputStream(MessageInputStream):

    def __init__(self, connection: Connection):
        self.connection = connection

    async def read(self) -> Optional[Message]:
        return await self.connection.read()

    async def _acquire(self) -> NoReturn:
        await self.connection.acquire()
        register(self.connection, self)

    async def _release(self) -> NoReturn:
        await self.connection.release(force=False)
