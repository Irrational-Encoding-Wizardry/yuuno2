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
import time
from asyncio import get_running_loop, wait_for
from asyncio import sleep, TimeoutError

from aiounittest import AsyncTestCase

from yuuno2.networking.base import Message, Connection
from yuuno2.networking.pipe import pipe


class TestPipeNetworking(AsyncTestCase):

    async def test_connection_receive(self):
        pc = Connection(*pipe())
        m = Message({}, [])
        async with pc:
            await pc.write(m)
            self.assertIs(m, await pc.read())

    async def test_connection_receive_twice(self):
        pc = Connection(*pipe())
        m = Message({}, [])
        async with pc:
            await pc.write(m)
            self.assertIs(m, await pc.read())
            with self.assertRaises(TimeoutError):
                await wait_for(pc.read(), 1)

    async def test_connection_wait(self):
        pc = Connection(*pipe())
        async with pc:
            await pc.close()
            self.assertIsNone(await pc.read())

    async def test_connection_read_with_wait(self):
        pc = Connection(*pipe())
        m = Message({}, [])

        async def _concurrent():
            t0 = time.time()
            self.assertIs(m, await pc.read())
            t1 = time.time()
            self.assertGreaterEqual(t1-t0, 1)

        async with pc:
            task = get_running_loop().create_task(_concurrent())
            await sleep(1)
            await pc.write(m)
            await task

    async def test_connection_close_with_wait(self):
        pc = Connection(*pipe())
        m = Message({}, [])

        async def _concurrent():
            t0 = time.time()
            with self.assertRaises(TimeoutError):
                await pc.read()
            t1 = time.time()
            self.assertGreaterEqual(t1-t0, 1)

        async with pc:
            task = get_running_loop().create_task(_concurrent())
            await sleep(1.2)
            await pc.close()
            await task