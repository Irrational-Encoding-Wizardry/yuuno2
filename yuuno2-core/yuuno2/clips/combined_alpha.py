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
from asyncio import gather
from typing import Mapping, Union, NoReturn

from yuuno2.clip import Clip, Frame
from yuuno2.format import RawFormat, Size, ColorFamily
from yuuno2.resource_manager import register
from yuuno2.typings import Buffer


class AlphaFrame(Frame):
    def __init__(self, main: Frame, alpha: Frame):
        self.main = main
        self.alpha = alpha

    @property
    def size(self) -> Size:
        return self.main.size

    @property
    def native_format(self) -> RawFormat:
        nf = self.main.native_format

        if not nf.planar:
            return nf

        return nf._replace(num_fields=nf.num_fields+1)

    async def can_render(self, format: RawFormat) -> bool:
        await self.ensure_acquired()

        if format == self.main.native_format:
            return True

        if not format.planar:
            return False

        if format.num_planes not in (2, 4):
            return (await self.main.can_render(format))

        main_f = format._replace(num_fields=format.num_fields-1)
        alpha_f = format._replace(num_fields=1, family=ColorFamily.GREY)
        return all(await gather(self.main.can_render(main_f), self.alpha.can_render(alpha_f)))

    async def render_into(self, buffer: Buffer, plane: int, format: RawFormat, offset: int = 0) -> int:
        await self.ensure_acquired()

        if not (await self.can_render(format)):
            raise ValueError("Unsupported format.")

        if format.num_planes not in (2, 4):
            return (await self.main.render_into(buffer, plane, format, offset))

        main_f = format._replace(num_fields=format.num_fields-1)
        alpha_f = format._replace(num_fields=1, family=ColorFamily.GREY)
        if format.num_planes-1 == plane:
            return (await self.alpha.render_into(buffer, 0, alpha_f, offset))
        else:
            return (await self.main.render_into(buffer, plane, main_f, offset))

    async def get_metadata(self) -> Mapping[str, Union[int, str, bytes]]:
        await self.ensure_acquired()

        md_main, md_alpha = await gather(self.main.get_metadata(), self.alpha.get_metadata())
        metadata = dict(md_alpha)
        metadata.update(md_main)
        return metadata

    async def _acquire(self) -> NoReturn:
        await gather(self.main.acquire(), self.alpha.acquire())
        register(self.main, self)
        register(self.alpha, self)

    async def _release(self) -> NoReturn:
        await gather(self.main.release(force=False), self.alpha.release(force=False))
        self.main = None
        self.alpha = None


class AlphaClip(Clip):

    def __init__(self, main: Clip, alpha: Clip):
        self.main = main
        self.alpha = alpha

    def __getitem__(self, item) -> Frame:
        return AlphaFrame(self.main[item], self.alpha[item])

    async def get_metadata(self) -> Mapping[str, Union[int, str, bytes]]:
        md_main, md_alpha = await gather(self.main.get_metadata(), self.alpha.get_metadata())
        metadata = dict(md_alpha)
        metadata.update(md_main)
        return metadata

    async def _acquire(self) -> NoReturn:
        await gather(self.main.acquire(), self.alpha.acquire())
        register(self.main, self)
        register(self.alpha, self)

    async def _release(self) -> NoReturn:
        await gather(self.main.release(force=False), self.alpha.release(force=False))
        self.main = None
        self.alpha = None

