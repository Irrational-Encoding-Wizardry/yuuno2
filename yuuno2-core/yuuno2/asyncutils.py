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
from asyncio import ensure_future, Future, wait, FIRST_COMPLETED, CancelledError, TimeoutError
from typing import TypeVar, Awaitable, Any, Union, NoReturn

T = TypeVar("T")
V = TypeVar("V")


async def suppress_cancel(future: 'Future[Any]') -> NoReturn:
    try:
        await future
    except CancelledError:
        pass


async def dynamic_timeout(main: Awaitable[T], closed: Awaitable[Any]) -> T:
    f_main:   Future[T]   = ensure_future(main)
    f_closed: Future[Any] = ensure_future(closed)

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
    f_a: Future[T] = ensure_future(a)
    f_b: Future[T] = ensure_future(b)
    await wait([f_a, f_b], return_when=FIRST_COMPLETED)
    if f_a.done():
        f_b.cancel()
        return f_a.result()
    else:
        f_a.cancel()
        return f_b.result()

