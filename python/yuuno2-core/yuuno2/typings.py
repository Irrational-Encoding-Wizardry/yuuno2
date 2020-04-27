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
from typing import Union, TypeVar, Mapping, Sequence, Any


T = TypeVar("T")


Buffer = Union[bytearray, memoryview]
ConfigTypes = Union[bytes, str, int, float, None]

JSONValue = Union[str, int, float, bool, None, Mapping[str, 'JSONValue'], Sequence['JSONValue']]
JSON = Union[Mapping[str, JSONValue], Sequence[JSONValue]]