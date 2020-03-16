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
from yuuno2.tests.mocks import MockScript
from yuuno2.providers.single import SingleScriptProvider


class TestSingleScript(AsyncTestCase):

    async def test_non_owned(self):
        script = MockScript()
        single = SingleScriptProvider(script)
        async with script:
            async with single:
                pass
            self.assertTrue(script.acquired)

    async def test_owner(self):
        script = MockScript()
        single = SingleScriptProvider(script)
        async with single:
            self.assertTrue(script.acquired)
        self.assertFalse(script.acquired)

    async def test_always_same(self):
        script = MockScript()
        single = SingleScriptProvider(script)
        async with single:
            self.assertIs(script, await single.get())
            self.assertIs(script, await single.get())
