from asyncio import coroutine, Task, Event, wait_for
from typing import Optional

from aiounittest import AsyncTestCase

from yuuno2.networking.base import Message
from yuuno2.networking.pipe import pipe
from yuuno2.networking.reader import ReaderTask


class TestNetworkingReader(AsyncTestCase):

    async def test_run_after_release(self):
        task: Optional[Task] = None
        pipe_r, pipe_w = pipe()
        reader = ReaderTask(pipe_r, coroutine(lambda m: None))
        async with reader:
            task = reader._task
            self.assertIsNotNone(task)
            self.assertFalse(task.done())
        self.assertTrue(task.done())

    async def test_receiving_messages(self):
        m1 = Message({}, [])
        m2 = Message({}, [])
        messages = []
        finished = Event()

        async def _r(m: Message):
            messages.append(m)
            if len(m) == 2:
                finished.set()

        pipe_r, pipe_w = pipe()
        reader = ReaderTask(pipe_r, _r)
        async with reader, pipe_w:
            await pipe_w.write(m1)
            await pipe_w.write(m2)
            await wait_for(finished.wait(), 5)

        self.assertIs(m1, messages[0])
        self.assertIs(m2, messages[1])
