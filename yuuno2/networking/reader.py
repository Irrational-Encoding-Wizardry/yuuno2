from asyncio import Task, get_running_loop, CancelledError
from typing import Optional, NoReturn, Awaitable, Callable, Any

from yuuno2.networking.base import MessageInputStream, Message
from yuuno2.resource_manager import Resource, register


class ReaderTask(Resource):

    def __init__(self, input: MessageInputStream, callback: Callable[[Optional[Message]], Awaitable[Any]]):
        self.input = input
        self.callback = callback
        self._task: Optional[Task] = None
        self._remote_shutdown = False

    async def run(self):
        while True:
            message: Optional[Message] = await self.input.read()
            await self.callback(message)
            if message is None:
                break

        self._remote_shutdown = True

    async def _acquire(self) -> NoReturn:
        self._task = get_running_loop().create_task(self.run())
        register(self.input, self)

    async def _release(self) -> NoReturn:
        _c_cancelled_manually = False
        if not self._remote_shutdown:
            self._task.cancel()
            _c_cancelled_manually = True

        if not self._task.done():
            if _c_cancelled_manually:
                try:
                    await self._task
                except CancelledError:
                    pass
            else:
                await self._task

        self.callback = None

