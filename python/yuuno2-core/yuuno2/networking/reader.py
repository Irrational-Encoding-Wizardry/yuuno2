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
