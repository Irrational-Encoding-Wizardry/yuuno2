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
import io

from yuuno2.resource_manager import _resources


def to_dot() -> str:
    f = io.StringIO()
    print("digraph Resources {", file=f)
    print("  node [shape=record]", file=f)

    d = dict(_resources)
    for k, v in d.items():
        r = repr(k).replace("<", "\\<").replace(">", "\\>")
        color = "#ff0000" if v.released else "#000000"
        fill = 'fill="#00ffff"' if v.parent_dead else ''
        print(f'  o{id(k)} [label="{r} | {v.acquired}" color="{color}" {fill}]', file=f)

    for k, v in d.items():
        for c in v.children:
            print(f'  o{id(k)} -> o{id(c)}', file=f)

    print("}", file=f)

    return f.getvalue()
