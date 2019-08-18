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

from yuuno2.providers.single import SingleScriptProvider
from yuuno2.providers.switched import SwitchedScriptProvider
from yuuno2.tests.mocks import MockScript


class TestSwitchedProvider(AsyncTestCase):

    async def test_fail_no_type(self):
        s1 = MockScript()
        sp1 = SingleScriptProvider(s1)

        s2 = MockScript()
        sp2 = SingleScriptProvider(s2)

        switched = SwitchedScriptProvider(sp1=sp1, sp2=sp2)
        async with switched:
            self.assertIsNone(await switched.get())

    async def test_fail_unknown_type(self):
        s1 = MockScript()
        sp1 = SingleScriptProvider(s1)

        s2 = MockScript()
        sp2 = SingleScriptProvider(s2)

        switched = SwitchedScriptProvider(sp1=sp1, sp2=sp2)
        async with switched:
            self.assertIsNone(await switched.get(type="sp_unknown"))

    async def test_get_s1(self):
        s1 = MockScript()
        sp1 = SingleScriptProvider(s1)

        s2 = MockScript()
        sp2 = SingleScriptProvider(s2)

        switched = SwitchedScriptProvider(sp1=sp1, sp2=sp2)
        async with switched:
            self.assertIs(await switched.get(type="sp1"), s1)

    async def test_get_s2(self):
        s1 = MockScript()
        sp1 = SingleScriptProvider(s1)

        s2 = MockScript()
        sp2 = SingleScriptProvider(s2)

        switched = SwitchedScriptProvider(sp1=sp1, sp2=sp2)
        async with switched:
            self.assertIs(await switched.get(type="sp2"), s2)

    async def test_switch_flag_changed(self):
        s1 = MockScript()
        sp1 = SingleScriptProvider(s1)

        s2 = MockScript()
        sp2 = SingleScriptProvider(s2)

        switched = SwitchedScriptProvider(sp1=sp1, sp2=sp2, _switch="test")
        async with switched:
            self.assertIs(await switched.get(test="sp2"), s2)