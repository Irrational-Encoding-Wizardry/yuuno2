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
import json
import array
import itertools
import sys
from abc import abstractmethod, ABC
from asyncio import Queue
from typing import NoReturn, Optional

from yuuno2.networking.base import Message, MessageOutputStream, MessageInputStream
from yuuno2.sans_io import protocol, read_exactly, emit, Consumer


@protocol
async def bytes_protocol():
    try:
        while True:
            sz: bytes = await read_exactly(4)
            length = int.from_bytes(sz, 'big')

            hdr = await read_exactly(length*4)
            ary = array.array('L')
            ary.frombytes(hdr)
            if sys.byteorder != "big":
                ary.byteswap()

            text, *buffers = [(await read_exactly(l)) for l in ary]

            text = text.decode("utf-8")
            text = json.loads(text)

            await emit(Message(text, buffers))
    except ConnectionResetError:
        pass


class ByteOutputStream(MessageOutputStream, ABC):

    @staticmethod
    def write_message(message: Message) -> bytes:
        parts = [None]

        text, buffers = message
        parts.append(json.dumps(text, ensure_ascii=True, separators=(',', ':')).encode("utf-8"))
        parts.extend(buffers)

        hdr = array.array(
            'L',
            [len(parts)-1] + [len(part) for part in itertools.islice(parts, 1, None, None)]
        )
        if sys.byteorder != "big":
            hdr.byteswap()
        parts[0] = hdr.tobytes()

        return b''.join(parts)

    @abstractmethod
    async def send(self, data: bytes) -> None:
        pass

    async def write(self, message: Message) -> NoReturn:
        await self.send(self.write_message(message))


class ByteInputStream(MessageInputStream, ABC):

    def __init__(self, maxsize=50):
        self.protocol: Consumer[Message] = bytes_protocol()
        self.queue = Queue(maxsize=maxsize)
        self._queue_is_full = False

    def continue_running(self):
        self.feed(b"")

    def queue_filled(self):
        pass

    def queue_active(self):
        pass

    def feed(self, data: bytes):
        for message in self.protocol.feed(data):
            if self.queue.full():
                return

            self.queue.put_nowait(message)
            if self.queue.full():
                self._queue_is_full = True
                self.queue_filled()
                return

        if not self.queue.full() and self._queue_is_full:
            self._queue_is_full = False
            self.queue_active()

    async def read(self) -> Optional[Message]:
        if self.queue.empty():
            await self.ensure_acquired()

        read = (await self.queue.get())
        self.continue_running()
        return read
