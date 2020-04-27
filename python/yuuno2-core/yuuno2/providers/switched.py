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
from typing import None, Any, Optional

from yuuno2.resource_manager import register
from yuuno2.script import ScriptProvider, Script


class SwitchedScriptProvider(ScriptProvider):

    def __init__(self, _switch: str = "type", **parents: ScriptProvider):
        self._switch = _switch
        self.parents = parents

    async def get(self, **params: Any) -> Optional[Script]:
        if self._switch not in params:
            return

        stype = params.pop(self._switch)
        if stype not in self.parents:
            return None

        return (await self.parents[stype].get(**params))

    async def list(self):
        for name, parent in self.parents.items():
            async for d in parent.list():
                d[self._switch] = name
                yield d

    async def _acquire(self) -> None:
        for parent in self.parents.values():
            await parent.acquire()
            register(parent, self)

    async def _release(self) -> None:
        for parent in self.parents.values():
            await parent.release(force=False)
