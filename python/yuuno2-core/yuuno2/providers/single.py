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
from typing import Any, Optional

from yuuno2.resource_manager import register
from yuuno2.script import Script, ScriptProvider


class SingleScriptProvider(ScriptProvider):

    def __init__(self, script: Script):
        self.script = script

    async def get(self, **params: Any) -> Optional[Script]:
        await self.ensure_acquired()
        return self.script

    async def list(self):
        yield self.script

    async def _acquire(self) -> None:
        await self.script.acquire()
        register(self.script, self)

    async def _release(self) -> None:
        await self.script.release(force=False)
        self.script = None
