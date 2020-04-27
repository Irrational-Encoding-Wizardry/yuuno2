#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2018,2019 StuxCrystal (Roland Netzsch <stuxcrystal@encode.moe>)
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
from typing import None, Any, Optional

from yuuno2.resource_manager import register
from yuuno2.script import ScriptProvider, Script
from yuuno2.vapoursynth.script import VapourSynthScript
from yuuno2.vapoursynth.vsscript.vs_capi import ScriptEnvironment
from yuuno2.vapoursynth.vsscript.vs_capi import enable_vsscript, disable_vsscript


class VSScript(VapourSynthScript):

    def __init__(self, provider: ScriptProvider):
        self.provider = provider
        # noinspection PyTypeChecker
        super().__init__(None)

    async def _acquire(self) -> None:
        register(self.provider, self)
        self.script_environment = ScriptEnvironment()
        self.script_environment.enable()

        self.environment = self.script_environment.environment()
        await super()._acquire()

    async def _release(self) -> None:
        await super()._release()
        if self.script_environment is not None:
            self.script_environment.dispose()
            self.script_environment = None
            self.environment = None


_counter = 0


class VSScriptProvider(ScriptProvider):
    async def get(self, **params: Any) -> Optional[Script]:
        return VSScript(self)

    async def _acquire(self) -> None:
        global _counter
        if _counter == 0:
            enable_vsscript()
        _counter += 1

    async def _release(self) -> None:
        global _counter
        _counter -= 1
        if _counter == 0:
            disable_vsscript()
