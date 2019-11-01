#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2019 StuxCrystal (Roland Netzsch <stuxcrystal@encode.moe>)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from asyncio import coroutine, Task, Event, wait_for
from typing import Optional

from aiounittest import AsyncTestCase

from yuuno2.networking.base import Message
from yuuno2.networking.pipe import pipe
from yuuno2.networking.reader import ReaderTask


async def noop(*_, **__): return None


class TestNetworkingReader(AsyncTestCase):

    async def test_run_after_release(self):
        task: Optional[Task] = None
        pipe_r, pipe_w = pipe()
        reader = ReaderTask(pipe_r, noop)
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
