from asyncio import Queue, Event, ALL_COMPLETED, wait, ensure_future
from typing import NoReturn, Optional, Tuple, Awaitable

from yuuno2.asyncutils import dynamic_timeout
from yuuno2.networking.base import MessageInputStream, Message, MessageOutputStream, Connection
from yuuno2.resource_manager import Resource, register


class PipeData(Resource):

    def __init__(self):
        self._tasks = set()
        self.queue = Queue()
        self.closed = Event()

    def next_message(self) -> Awaitable[Optional[Message]]:
        task = ensure_future(self.queue.get())
        self._tasks.add(task)
        task.add_done_callback(lambda f: self._tasks.remove(task))
        return task

    async def _acquire(self) -> NoReturn:
        pass

    async def _release(self) -> NoReturn:
        self.closed.set()
        if len(self._tasks) > 0:
            for t in self._tasks:
                t.cancel()
            await wait(self._tasks, return_when=ALL_COMPLETED)


class PipeInputStream(MessageInputStream):

    def __init__(self, pipe: PipeData):
        self.pipe = pipe

    async def read(self) -> Optional[Message]:
        if not self.pipe.queue.empty():
            return self.pipe.queue.get_nowait()

        if self.pipe.closed.is_set():
            return None

        return (await dynamic_timeout(self.pipe.next_message(), self.pipe.closed.wait()))

    async def _acquire(self) -> NoReturn:
        await self.pipe.acquire()
        register(self.pipe, self)

    async def _release(self) -> NoReturn:
        await super()._release()
        await self.pipe.release(force=False)
        self.pipe = None


class PipeOutputStream(MessageOutputStream):

    def __init__(self, pipe: PipeData):
        self.pipe = pipe

    async def write(self, message: Message) -> NoReturn:
        if self.pipe.closed.is_set():
            return

        await self.pipe.queue.put(message)

    async def close(self) -> NoReturn:
        self.pipe.closed.set()

    async def _acquire(self) -> NoReturn:
        await self.pipe.acquire()
        register(self.pipe, self)

    async def _release(self) -> NoReturn:
        if not self.pipe.closed.set():
            await self.close()

        await super()._release()
        await self.pipe.release(force=False)
        self.pipe = None


def pipe() -> Tuple[PipeInputStream, PipeOutputStream]:
    data = PipeData()
    return (
        PipeInputStream(data),
        PipeOutputStream(data)
    )


def pipe_bidi() -> Tuple[Connection, Connection]:
    p1 = PipeData()
    p2 = PipeData()

    c1 = Connection(
        PipeInputStream(p1),
        PipeOutputStream(p2)
    )
    c2 = Connection(
        PipeInputStream(p2),
        PipeOutputStream(p1)
    )
    return c1, c2