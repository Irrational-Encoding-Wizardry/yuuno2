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
