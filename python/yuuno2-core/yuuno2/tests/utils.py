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
from functools import wraps
from asyncio import wait_for, get_running_loop
from yuuno2.asyncutils import register_event_loop, clear_event_loop


def with_registered_yuuno(func):
    @wraps(func)
    async def _wrapper(self, *args, **kwargs):
        register_event_loop(get_running_loop())
        try:
            return await func(self, *args, **kwargs)
        finally:
            clear_event_loop()
    return _wrapper


class timeout_context(object):

    def __init__(self, ctm, after: float):
        self.ctm = ctm
        self.after = after

    async def __aenter__(self):
        return await wait_for(self.ctm.__aenter__(), self.after)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await wait_for(self.ctm.__aexit__(exc_type, exc_val, exc_type), self.after)


class force_release(object):

    def __init__(self, resource):
        self.resource = resource

    async def __aenter__(self):
        await self.resource.acquire()
        return self.resource

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.resource.acquired:
            await self.resource.release()
