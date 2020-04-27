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
import functools
from types import new_class
from collections import deque
from typing import Coroutine, TypeVar, Generic, Optional, Iterator, Any, Callable, Type, Awaitable


class Buffer(object):

    def __init__(self):
        self._size = 0
        self._cursor = 0
        self._buffer = deque()

        self._closed = False

    def _get_fragment(self) -> bytes:
        if not self._buffer:
            return b''

        part = self._buffer.popleft()
        if self._cursor > 0:
            return part[self._cursor:]
        else:
            return part

    def _read(self, length: int = 0) -> bytes:
        if len(self._buffer) == 0:
            return b''

        if length == 0:
            first = self._get_fragment()

            self._cursor = 0
            self._size = 0

            if len(self._buffer) == 0:
                return first

            data = b''.join([first] + list(self._buffer))
            self._buffer.clear()
            return data

        parts = []
        while length > 0 and len(self._buffer) > 0:
            part = self._buffer.popleft()

            if len(part) > self._cursor+length:
                self._buffer.appendleft(part)
                part = part[self._cursor:self._cursor+length]
                parts.append(part)
                self._cursor += length
                break

            if self._cursor > 0:
                part = part[self._cursor:]

            parts.append(part)
            length -= len(part)
            self._cursor = 0

        result = b''.join(parts)
        self._size -= len(result)
        return result

    def peek(self, length: int = 0) -> Optional[bytes]:
        if len(self._buffer) == 0 and self._closed:
            return None

        data = self._read(length)

        fragment = self._get_fragment()
        if fragment:
            self._buffer.appendleft(fragment)

        if data:
            self._buffer.appendleft(data)
            self._size += len(data)

        return data

    def read(self, length: int = 0) -> Optional[bytes]:
        if len(self._buffer) == 0 and self._closed:
            return None

        return self._read(length)

    def feed(self, data: Optional[bytes]) -> None:
        if self._closed:
            if data is None:
                return

            raise IOError("Feeding closed buffer.")

        if data is None:
            self.close()
            return

        if len(data) == 0:
            return

        self._buffer.append(data)
        self._size += len(data)

    def close(self) -> None:
        self._closed = True

    @property
    def closing(self) -> bool:
        return self._closed

    @property
    def closed(self) -> bool:
        return len(self) == 0 and self.closing

    def __len__(self):
        return self._size


T = TypeVar("T")
A = TypeVar("A")


class PauseProtocol(BaseException):
    def __init__(self, value: Any):
        self.value = value


class EmitEvent(BaseException):
    def __init__(self, value: Any):
        self.value = value


class _Action(Generic[A]):

    def __await__(self) -> A:
        return (yield self)

    def handle(self, consumer: 'Consumer') -> Optional[A]:
        pass

    @classmethod
    def operation(cls: '_Action[A]', func: Callable[..., Optional[A]]) -> Type['_Action[A]']:
        def _init(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def _handle(self, consumer):
            return func(consumer, *self.args, *self.kwargs)

        return new_class(
            func.__name__,
            (cls, ),
            {},
            lambda ns: ns.update({'__init__':_init, 'handle': _handle})
        )


class Consumer(Generic[A]):

    _return = _Action.operation(lambda _, v: v)

    def __init__(self, coro: Coroutine):
        self.buffer = Buffer()
        self._queue = [self._return(None)]

        self._closed = False

        self.coro = coro
        self._init_events = []
        self._init_events = list(self.feed(b""))

    @property
    def closed(self):
        return self._closed or self.buffer.closed

    @property
    def closing(self):
        return self.closed or self.buffer.closing

    def _next(self) -> Optional[_Action]:
        if len(self._queue) == 0:
            return None
        return self._queue.pop()

    def feed(self, data: Optional[bytes]) -> Iterator[A]:
        # Ignore closed protocols.
        if self.closing:
            if data:
                raise IOError("Protocol has finished.")
        else:
            # Feed the buffer.
            if data is None:
                self.buffer.close()
            else:
                self.buffer.feed(data)

        return self._execute()

    def _execute(self) -> Iterator[A]:
        # Run pre-stored events.
        ie = self._init_events
        self._init_events = []
        yield from iter(ie)

        # Fill data.
        for op in iter(self._next, None):
            try:
                next_op = self.coro.send(op.handle(self))
            except PauseProtocol as e:
                self._queue.append(self._return(e.value))
                break
            except EmitEvent as e:
                self._queue.append(self._return(None))
                yield e.value
            except StopIteration:
                self._closed = True
                break
            except Exception:
                self._closed = True
                raise
            else:
                self._queue.append(next_op)

    def close(self) -> Iterator[A]:
        return self.feed(None)


def protocol(func: Callable[..., Awaitable[_Action]]) -> Callable[..., Consumer]:
    @functools.wraps(func)
    def _wrapped(*args, **kwargs):
        coro = func(*args, **kwargs)
        return Consumer(coro)
    return _wrapped


# Base Operations
@_Action.operation
def sleep(consumer: Consumer) -> bool:
    if consumer.buffer.closing:
        return False
    raise PauseProtocol(True)


@_Action.operation
def emit(_: Consumer, value: Any) -> None:
    raise EmitEvent(value)


# Buffer Control
@_Action.operation
def peek(consumer: Consumer, length: int = 0) -> bytes:
    return consumer.buffer.peek(length)


@_Action.operation
def read(consumer: Consumer, length: int = 0) -> bytes:
    return consumer.buffer.read(length)


@_Action.operation
def left(consumer: Consumer) -> int:
    return len(consumer.buffer)


@_Action.operation
def close(consumer: Consumer) -> None:
    consumer.buffer.close()


@_Action.operation
def closing(consumer: Consumer) -> bool:
    return consumer.buffer.closing


# Mid-Level commands
async def wait(length: int = 1) -> None:
    while (await left()) < length:
        if not (await sleep()):
            # Buffer is closing. Prevent sleeping.
            return


async def read_exactly(length: int = 1) -> bytes:
    await wait(length)
    data = await read(length)
    if data is None or len(data) < length:
        raise ConnectionResetError
    return data
