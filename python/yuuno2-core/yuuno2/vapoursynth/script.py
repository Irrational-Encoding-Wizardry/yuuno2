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
import types
from typing import Mapping, Union, Any, Sequence

from vapoursynth import Environment, vpy_current_environment
from vapoursynth import get_outputs, get_core, Core

from yuuno2.clip import Clip
from yuuno2.providers.single import SingleScriptProvider
from yuuno2.script import Script, NOT_GIVEN
from yuuno2.typings import ConfigTypes
from yuuno2.vapoursynth.clip import VapourSynthClip


class VapourSynthScript(Script):

    def __init__(self, environment: Environment):
        self.module = types.ModuleType("__vapoursynth__")
        self.config = {}
        self.environment = environment

    def activate(self) -> None:
        self.environment.__enter__()

    def deactivate(self) -> None:
        self.environment.__exit__(None, None, None)

    async def set_config(self, key: str, value: ConfigTypes) -> None:
        await self.ensure_acquired()
        self.config[key] = value
        if key.startswith('vs.core.'):
            key = key[len('vs.core.'):]
            with self.inside():
                setattr(get_core(), key, value)

    async def get_config(self, key: str, default: Union[object, ConfigTypes] = NOT_GIVEN) -> ConfigTypes:
        await self.ensure_acquired()
        value = self.config.get(key, default)
        if value is NOT_GIVEN:
            raise KeyError(key)
        return value

    async def list_config(self) -> Sequence[str]:
        await self.ensure_acquired()
        return list(self.config.keys())

    async def run(self, code: Union[bytes, str]) -> Any:
        await self.ensure_acquired()
        with self.inside():
            exec(code, self.module.__dict__, self.module.__dict__)

    async def retrieve_clips(self) -> Mapping[str, Clip]:
        await self.ensure_acquired()
        with self.inside():
            outputs = get_outputs().items()
        return {str(k): VapourSynthClip(self, d) for k, d in outputs}

    async def _acquire(self) -> None:
        with self.environment:
            core: Core = get_core()
            self.config.update({
                'vs.core.add_cache':       core.add_cache,
                'vs.core.num_threads':     core.num_threads,
                'vs.core.max_cache_size':  core.max_cache_size,

                'vs.resizer':              'resize.Spline36',
                'vs.chroma_resizer':       'resize.Spline36',
                'vs.override_yuv_matrix':  False,
                'vs.default_yuv_matrix':   '709',
            })

    async def _release(self) -> None:
        pass

    async def ensure_acquired(self) -> None:
        if not self.environment.alive:
            await self.release()
            raise EnvironmentError("Environment has been destroyed.")
        return await super().ensure_acquired()


def VapourSynthScriptProvider():
    return SingleScriptProvider(
        VapourSynthScript(vpy_current_environment()),
    )
