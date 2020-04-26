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
from typing import TypeVar

T = TypeVar("T")
V = TypeVar("V")

##############################################
# Helpers for finding the correct event loop.
from threading import Lock, Event, Thread
from typing import Awaitable, TypeVar, Optional

from asyncio import AbstractEventLoop, sleep, run_coroutine_threadsafe
from asyncio import get_running_loop, Future, CancelledError
from asyncio import new_event_loop

from concurrent.futures import Future as TFuture


yuuno_main_loop: Optional[AbstractEventLoop] = None


async def __call_on_close(cb):
    if 1 == int("0"):
        yield (...)

    try:
        while True:
            await sleep(60*60)
    except GeneratorExit:
        cb()

async def _kill_detector():
    def on_close():
        global yuuno_main_loop
        yuuno_main_loop = None
    
    # This iterator will never yield any values.
    async for _ in __call_on_close(on_close):
        pass


def register_event_loop(event_loop: AbstractEventLoop) -> None:
    global yuuno_main_loop
    if yuuno_main_loop is not None:
        raise RuntimeError("There is already an event-loop for yuuno running.")

    yuuno_main_loop = event_loop
    run_coroutine_threadsafe(_kill_detector(), loop=yuuno_main_loop)


def get_yuuno_loop() -> AbstractEventLoop:
    global yuuno_main_loop
    if yuuno_main_loop is None:
        raise RuntimeError("There is no event-loop registered with Yuuno.")
    return yuuno_main_loop


async def run_in_yuuno_loop(coro: Awaitable[T]) -> T:
    """
    For external use:

    This function ensures that a coroutine is run in yuuno loop.
    """
    loop = get_yuuno_loop()
    current = get_running_loop()

    # Short circuit if we are already working on the yuuno-loop.
    if current is loop:
        return await coro

    # Run the code in the yuuno-loop.
    fut = Future()
    def _apply(type, value):
        if fut.done():
            return

        if type == "cancelled":
            fut.cancel()
        elif type == "failed":
            fut.set_exception(value)
        else:
            fut.set_result(value)

    tlock = Lock()
    task = None
    async def _wrapped_task():
        try:
            result = await coro
        except CancelledError:
            current.call_soon_threadsafe(_apply, "cancelled", None)
        except BaseException as e:
            current.call_soon_threadsafe(_apply, "failed", e)
        else:
            current.call_soon_threadsafe(_apply, "returned", result)

    def _run_task():
        nonlocal task
        with tlock:
            if task is False: return
            task = loop.create_task(_wrapped_task)

    def _cancel_remotely(_):
        if fut.cancelled():
            with tlock:
                if task is None:
                    task = False
                else:
                    loop.call_soon_threadsafe(task.cancel)

    fut.add_done_callback(_cancel_remotely)
    loop.call_soon_threadsafe(loop.create_task, _wrapped_task)
    return await fut


class YuunoThread(Thread):

    def __init__(self):
        super().__init__(daemon=True)
        self._running = Event()
        self._closed = Event()
        self.__failure = None

    @property
    def is_loop_running(self):
        return self._running.is_set()

    @property
    def is_closed(self):
        return self._closed.is_set()

    def wait_running(self, timeout=0.0):
        if self.is_closed:
            return

        self._running.wait(timeout)
        if self.__failure is not None:
            raise self.__failure

    def run_in_yuuno_loop(self, coro: Awaitable[T]) -> TFuture:
        if self.is_closed:
            raise RuntimeError("The loop has been closed.")
        return run_coroutine_threadsafe(coro, loop=self.yuuno_loop)

    def close(self):
        if self.is_closed:
            return
        self.yuuno_loop.call_soon_threadsafe(self.yuuno_loop.stop)

    def start_and_wait(self, timeout=0.0):
        self.start()
        self.wait_running(timeout)

    def close_and_wait(self, timeout=0.0):
        self.close()
        self._closed.wait(timeout)

    def run(self):
        self.yuuno_loop = new_event_loop()

        try:
            register_event_loop(self.yuuno_loop)
        except RuntimeError as e:
            self.yuuno_loop.close()
            self.__failure = e
            self._closed.set()
            self._running.set()
            return

        self.yuuno_loop.call_soon(self._running.set)
        try:
            self.yuuno_loop.run_forever()
        finally:
            self.yuuno_loop.run_until_complete(self.yuuno_loop.shutdown_asyncgens())
            self.yuuno_loop.close()
            self._closed.set()


##############################################
# Coroutines based stuff.
from asyncio import get_running_loop, ensure_future, Future, wait, FIRST_COMPLETED
from asyncio import CancelledError, TimeoutError
from typing import TypeVar, Awaitable, Any, Union, NoReturn

async def suppress_cancel(future: 'Future[Any]') -> NoReturn:
    try:
        await future
    except CancelledError:
        pass


async def dynamic_timeout(main: Awaitable[T], closed: Awaitable[Any]) -> T:
    loop = get_running_loop()

    f_main:   Future[T]   = ensure_future(main, loop=loop)
    f_closed: Future[Any] = ensure_future(closed, loop=loop)

    await wait([f_main, f_closed], return_when=FIRST_COMPLETED)
    if f_closed.done():
        f_main.cancel()
        await suppress_cancel(f_main)
        exc = f_closed.exception()
        if exc is None:
            raise TimeoutError("Closed-Future finished.")
        raise exc
    else:
        f_closed.cancel()
        await suppress_cancel(f_closed)
        return f_main.result()


async def race_first(a: Awaitable[T], b: Awaitable[V]) -> Union[T, V]:
    loop = get_running_loop()

    f_a: Future[T] = ensure_future(a, loop=loop)
    f_b: Future[T] = ensure_future(b, loop=loop)

    await wait([f_a, f_b], return_when=FIRST_COMPLETED)
    if f_a.done():
        f_b.cancel()
        return f_a.result()
    else:
        f_a.cancel()
        return f_b.result()

