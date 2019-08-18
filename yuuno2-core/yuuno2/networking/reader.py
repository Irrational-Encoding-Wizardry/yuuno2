from asyncio import Task, get_running_loop, CancelledError, TimeoutError
from typing import Optional, NoReturn, Awaitable, Callable, Any

from yuuno2.networking.base import MessageInputStream, Message
from yuuno2.resource_manager import Resource, register


class ReaderTask(Resource):

    def __init__(self, input: MessageInputStream, callback: Callable[[Optional[Message]], Awaitable[Any]]):
        self.input = input
        self.callback = callback

        self._initializing = True
        self._task: Optional[Task] = None

    async def run(self):
        while True:
            message: Optional[Message] = await self.input.read()

            if self.callback is None:
                return

            await self.callback(message)

            if message is None:
                break

    async def _acquire(self) -> NoReturn:
        self._task = get_running_loop().create_task(self.run())
        register(self.input, self)

    async def _release(self) -> NoReturn:
        if not self._task.done():
            self._task.cancel()

        self.callback = None

        try:
            await self._task
        except (CancelledError, TimeoutError):
            pass
