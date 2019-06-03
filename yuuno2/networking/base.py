from abc import ABC, abstractmethod
from asyncio import gather
from typing import NamedTuple, List, Mapping, Union, Optional, NoReturn

from yuuno2.resource_manager import Resource, NonAbcResource, register

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


class Connection(NonAbcResource, NamedTuple):
    input: MessageInputStream
    output: MessageOutputStream

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def _acquire(self):
        await gather(self.input.acquire(), self.output.acquire())
        register(self.input, self)
        register(self.output, self)

    async def _release(self):
        await gather(
            self.input.release(force=False),
            self.output.release(force=False)
        )

    async def close(self):
        await self.ensure_acquired()
        await self.output.close()

    async def write(self, message: Message):
        await self.ensure_acquired()
        await self.output.write(message)

    async def read(self) -> Optional[Message]:
        await self.ensure_acquired()
        return (await self.input.read())
