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
from aiounittest import AsyncTestCase
from yuuno2.providers.named import NamedScriptProvider
from yuuno2.tests.mocks import MockScriptProvider


class TestNamedScriptProvider(AsyncTestCase):

    async def test_unknown_script(self):
        sp = MockScriptProvider()
        named = NamedScriptProvider(sp)
        async with sp, named:
            self.assertIsNone(await named.get(name="unknown"))

    async def test_anonymous_script(self):
        sp = MockScriptProvider()
        named = NamedScriptProvider(sp)
        async with sp, named:
            self.assertIsNotNone(await named.get())

    async def test_create_script(self):
        sp = MockScriptProvider()
        named = NamedScriptProvider(sp)
        async with sp, named:
            script = await named.get(name="named", create=True)
            self.assertIsNotNone(script)
            self.assertIs(script, await named.get(name="named"))

    async def test_destroy_script(self):
        sp = MockScriptProvider()
        named = NamedScriptProvider(sp)
        async with sp, named:
            script = await named.get(name="named", create=True)
            await script.acquire()
            await script.release()
            self.assertIsNone(await named.get(name="named"))

    async def test_destroy_children(self):
        sp = MockScriptProvider()
        named = NamedScriptProvider(sp)
        async with sp, named:
            script = await named.get(name="named", create=True)
            await script.acquire()
        self.assertFalse(script.acquired)