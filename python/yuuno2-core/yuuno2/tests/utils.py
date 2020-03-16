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
from asyncio import wait_for


class timeout_context(object):

    def __init__(self, ctm, after: float):
        self.ctm = ctm
        self.after = after

    async def __aenter__(self):
        return await wait_for(self.ctm.__aenter__(), self.after)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await wait_for(self.ctm.__aexit__(exc_type, exc_val, exc_type), self.after)
