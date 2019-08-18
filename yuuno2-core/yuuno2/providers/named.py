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
from typing import NoReturn, Any, Optional, MutableMapping

from yuuno2.resource_manager import register, on_release
from yuuno2.script import ScriptProvider, Script


class NamedScriptProvider(ScriptProvider):

    def __init__(self, parent: ScriptProvider):
        self.parent = parent

        self._scripts: MutableMapping[str, Script] = {}

    async def get(self, **params: Any) -> Optional[Script]:
        await self.ensure_acquired()

        name: Optional[str] = params.pop('name', None)
        if name is None:
            return await self.parent.get(**params)

        create: bool = params.pop('create', False)
        if name in self._scripts:
            return self._scripts[name]
        if not create:
            return None

        script = await self.parent.get(**params)
        register(self, script)
        self._scripts[name] = script
        on_release(script, lambda s: self._release_script(name))
        return script

    def _release_script(self, name: str):
        del self._scripts[name]

    async def _acquire(self) -> NoReturn:
        await self.parent.acquire()
        register(self.parent, self)

    async def _release(self) -> NoReturn:
        await self.parent.release(force=False)
        self.parent = None
