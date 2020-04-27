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
from asyncio import sleep, ensure_future, CancelledError, TimeoutError
from typing import Optional, Any

from aiounittest import AsyncTestCase
from yuuno2.asyncutils import dynamic_timeout


async def t_sleep(time: int, result: Any = None, exc: Optional[Exception] = None) -> None:
    await sleep(time)
    if exc is not None:
        raise exc
    return result

o1 = object()
e1 = ValueError()


class AsyncUtilsTest(AsyncTestCase):

    async def test_done_after_canel(self):
        wait = ensure_future(sleep(10))
        w2 = await sleep(1)
        wait.cancel()
        with self.assertRaises(CancelledError):
            await wait
        self.assertTrue(wait.done())


    async def test_dynamic_timeout_main_success(self):
        main = ensure_future(t_sleep(1, o1, None))
        fail = ensure_future(t_sleep(10))

        result = await dynamic_timeout(main, fail)
        self.assertTrue(main.done())
        self.assertTrue(fail.done())

        self.assertFalse(main.cancelled())
        self.assertTrue(fail.cancelled())

        self.assertIsNone(main.exception())
        self.assertIs(result, o1)

        fail.cancel()

    async def test_dynamic_timeout_main_failure(self):
        main = ensure_future(t_sleep(1, o1, e1))
        fail = ensure_future(t_sleep(10))

        with self.assertRaises(ValueError):
            result = await dynamic_timeout(main, fail)

        self.assertTrue(main.done())
        self.assertTrue(fail.done())

        self.assertFalse(main.cancelled())
        self.assertTrue(fail.cancelled())

        self.assertIs(e1, main.exception())

        fail.cancel()

    async def test_dynamic_timeout_fail_success(self):
        main = ensure_future(t_sleep(10, o1))
        fail = ensure_future(t_sleep(1))

        with self.assertRaises(TimeoutError):
            result = await dynamic_timeout(main, fail)

        self.assertTrue(main.done())
        self.assertTrue(fail.done())

        self.assertTrue(main.cancelled())
        self.assertFalse(fail.cancelled())

    async def test_dynamic_timeout_fail_failure(self):
        main = ensure_future(t_sleep(10, o1))
        fail = ensure_future(t_sleep(1, None, e1))

        with self.assertRaises(ValueError):
            result = await dynamic_timeout(main, fail)

        self.assertTrue(main.done())
        self.assertTrue(fail.done())

        self.assertTrue(main.cancelled())
        self.assertFalse(fail.cancelled())

        self.assertIs(e1, fail.exception())

