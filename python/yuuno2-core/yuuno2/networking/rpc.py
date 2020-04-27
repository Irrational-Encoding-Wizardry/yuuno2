import abc
from asyncio import coroutine, gather
from typing import Callable, Awaitable, Any

from yuuno2.networking.message import Message


class Handler(object):
    def __init__(self):
        super().__init__()

        self._counter: int = 0
        self.callbacks = {}

    @property
    def __next_id(self) -> int:
        val = self._counter
        self._counter += 1
        return val

    def create(self, cb: Callable[[...], Awaitable[Any]]) -> Callable[[], None]:
        num = self.__next_id
        self.callbacks[num] = coroutine(cb)
        return lambda: self.callbacks.pop(num, None)

    async def emit(self, *args, **kwargs) -> None:
        await gather(*(cb(*args, **kwargs) for cb in self.callbacks.values()))



class Connection(abc.ABC):
    @abc.abstractmethod
    async def send(self, msg: Message):
        pass

    @abc.abstractmethod
    def register_receiver(self,  )