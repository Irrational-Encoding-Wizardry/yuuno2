#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2020 StuxCrystal (Roland Netzsch <stuxcrystal@encode.moe>)
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
import abc
from asyncio import gather
from typing import Callable, Awaitable, Any, Optional, TypeVar, Generic, Tuple

from yuuno2.asyncutils import get_yuuno_loop, coroutine
from yuuno2.networking.message import Message
from yuuno2.resource_manager import Resource, NonAbcResource, register, on_release


T = TypeVar("T")


class _HandlerCb(Resource):
    __slots__ = ["e_cb", "r_cb"]

    def __init__(self, e_cb, r_cb):
        self.e_cb = e_cb
        self.r_cb = r_cb

    async def _emit(self, args, kwargs):
        return await self.e_cb(*args, **kwargs)

    async def _acquire(self):
        on_release(self, lambda _: self.r_cb())
    
    async def _release(self):
        self.r_cb = None
        self.e_cb = None


class Handler(NonAbcResource, Generic[T]):
    def __init__(self):
        super().__init__()

        self._counter: int = 0
        self.callbacks = {}

    @property
    def __next_id(self) -> int:
        val = self._counter
        self._counter += 1
        return val

    async def create(self, cb: Callable[[Optional[T]], Awaitable[None]]) -> Callable[[], Awaitable[None]]:
        num = self.__next_id
        cb = _HandlerCb(coroutine(cb), lambda: self.callbacks.pop(num, None))
        self.callbacks[num] = cb
        await cb.acquire()
        register(self, cb)
        return cb

    async def emit(self, *args, **kwargs) -> None:
        if not self.callbacks:
            return

        await gather(*(cb._emit(args, kwargs) for cb in self.callbacks.values()))

    async def _acquire(self):
        pass

    async def _release(self):
        self.callbacks = {}


class BaseConnection(Resource):
    @abc.abstractmethod
    async def send(self, msg: Optional[Message]):
        pass

    @abc.abstractmethod
    async def on_message(self, cb: Callable[[Optional[Message]], Awaitable[None]]) -> Callable[[], None]:
        pass


class MessageBus(BaseConnection):
    def __init__(self):
        super().__init__()
        self._handler: Handler[Message] = Handler()

    async def send(self, msg: Message) -> None:
        await self.ensure_acquired()
        await self._handler.emit(msg)

    async def on_message(self, cb) -> Callable[[], Awaitable[None]]:
        await self.ensure_acquired()
        cb = await self._handler.create(cb)
        register(self, cb)
        return cb

    async def _acquire(self):
        await self._handler.acquire()
        register(self, self._handler)

    async def _release(self):
        pass


class Connection(BaseConnection):

    def __init__(self, ingress: BaseConnection, egress: BaseConnection):
        super().__init__()
        self._ingress = ingress
        self._egress = egress

    async def send(self, msg: Message) -> None:
        await self.ensure_acquired()
        return await self._egress.send(msg)

    async def on_message(self, cb):
        self.ensure_acquired_sync()
        cb = await self._ingress.on_message(cb)
        register(self, cb)
        return cb

    async def _receive(self, msg: Optional[Message]) -> None:
        if msg is None:
            self._closed = True
        await self._handler.emit(msg)

    async def _acquire(self):
        await self._ingress.acquire()
        await self._egress.acquire()
        register(self._ingress, self)
        register(self._egress, self)
    
    async def _release(self):
        await self._ingress.release(force=False)
        await self._egress.release(force=False)


def pipe() -> Tuple[BaseConnection, BaseConnection]:
    mb1, mb2 = MessageBus(), MessageBus()
    return Connection(mb1, mb2), Connection(mb2, mb1)