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
from asyncio import Protocol, BaseTransport, get_running_loop, sleep, BaseProtocol
from asyncio import Queue, Event, Transport, ensure_future, TimeoutError
from typing import Optional, NoReturn
from weakref import WeakKeyDictionary

from yuuno2.asyncutils import dynamic_timeout
from yuuno2.networking.base import Message, MessageInputStream, MessageOutputStream
from yuuno2.networking.serializer import ByteOutputStream, bytes_protocol
from yuuno2.resource_manager import ResourceProxy, remove_callback, on_release


class ResourceDescriptor(object):

    def __init__(self):
        self._refs = WeakKeyDictionary()

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self._refs.get(instance, None)

    def _unset_by_expiry(self, rs):
        if isinstance(rs, ResourceProxy):
            rs = rs.target

        if rs in self._refs:
            del self._refs[rs]

    def __set__(self, instance, value):
        if instance in self._refs:
            prev = self._refs.pop(instance)
            if value is not None:
                remove_callback(prev, self._unset_by_expiry)

        self._refs[instance] = value
        if value is not None:
            on_release(value, self._unset_by_expiry)

    def __delete__(self, instance):
        if instance in self._refs:
            old = self._refs.pop(instance)
            if old is not None:
                remove_callback(old, self._unset_by_expiry)


class YuunoBaseProtocol(BaseProtocol):
    QUEUE_MAXSIZE = 30

    _ingress: Optional[MessageInputStream] = ResourceDescriptor()
    _egress: Optional[MessageOutputStream] = ResourceDescriptor()

    def __init__(self):
        self.transport: Optional[BaseTransport] = None
        self.protocol = bytes_protocol()
        self.rqueue = Queue()

        self._transport_gate = Event()
        self._closed = Event()

    async def _close(self):
        if self._ingress is not None:
            await self._ingress.release(force=True)
        if self._egress is not None:
            await self._egress.release(force=True)

    async def read_next_message(self) -> Optional[Message]:
        if self._closed.is_set():
            return

        try:
            message = await dynamic_timeout(self.rqueue.get(), self._closed.wait())
        except TimeoutError:
            return None
        else:
            if self.rqueue.qsize() < self.QUEUE_MAXSIZE:
                self.after_message_read()

            return message

    def after_message_read(self):
        pass

    async def write_message(self, message: Message):
        if self._closed.is_set():
            return

        try:
            await dynamic_timeout(self._transport_gate.wait(), self._closed.wait())
        except TimeoutError:
            return

        self.write_message_data(ByteOutputStream.write_message(message))

    def _parse_until(self, maxsize: Optional[int] = QUEUE_MAXSIZE):
        if maxsize is not None and self.rqueue.qsize()>=maxsize:
            return False

        for msg in self.protocol.feed(b""):
            self.rqueue.put_nowait(msg)
            if maxsize is not None and self.rqueue.qsize() >= maxsize:
                return False

        return True

    def write_message_data(self, data: bytes):
        raise NotImplementedError

    def feed(self, data: Optional[bytes]) -> bool:
        self.protocol.feed(data)
        return self._parse_until(self.QUEUE_MAXSIZE)

    def stop_writing(self):
        self._transport_gate.clear()

    def continue_writing(self):
        self._transport_gate.set()

    def finishing(self):
        if self._closed.set():
            return

        self._transport_gate.clear()
        self._closed.set()
        ensure_future(self._close(), loop=get_running_loop())
        self.feed(None)

    async def close(self):
        self.transport.close()


class YuunoProtocol(Protocol, YuunoBaseProtocol):
    transport: Transport

    def write_message_data(self, message):
        self.transport.write(message)

    def connection_made(self, transport: BaseTransport) -> None:
        # noinspection PyTypeChecker
        self.transport = transport
        self.continue_writing()

    def after_message_read(self):
        self.transport.resume_reading()

    def feed(self, data: Optional[bytes]):
        if not super().feed(data):
            self.transport.pause_reading()

    def data_received(self, data: bytes) -> None:
        self.feed(data)

    def pause_writing(self) -> None:
        self.stop_writing()

    def resume_writing(self) -> None:
        self.continue_writing()

    def connection_lost(self, exc: Optional[Exception]) -> None:
        self.finishing()


class ConnectionInputStream(MessageInputStream):

    def __init__(self, protocol: YuunoBaseProtocol):
        self.protocol = protocol

    async def read(self) -> Optional[Message]:
        return await self.protocol.read_next_message()

    async def _acquire(self) -> NoReturn:
        self.protocol._ingress = self

    async def _release(self) -> NoReturn:
        self.protocol._ingress = None


class ConnectionOutputStream(MessageOutputStream):

    def __init__(self, protocol: YuunoBaseProtocol):
        self.protocol = protocol

    async def write(self, message: Message) -> NoReturn:
        await self.protocol.write_message(message)
        await sleep(0)

    async def close(self) -> NoReturn:
        await self.protocol.close()

    async def _acquire(self) -> NoReturn:
        self.protocol._egress = self

    async def _release(self) -> NoReturn:
        if self.protocol._egress is self:
            await self.close()

        self.protocol._egress = None
