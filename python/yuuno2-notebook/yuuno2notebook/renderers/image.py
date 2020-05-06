# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017-2020 StuxCrystal (Roland Netzsch <stuxcrystal@encode.moe>)
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
from yuuno2.format import RGB24, RGBA32, RawFormat, Size

import io
import struct
import asyncio
from PIL.Image import register_save, frombuffer, merge
from PIL.PngImagePlugin import PngInfo, putchunk, _save

_EMPTY = []
FORMAT_NAME = "png+srgb.yuuno"

# These values are taken from the official PNG specification.
# These values allow older browsers to have sRGB-like color-settings.
GAMA_SRGB = struct.pack('!I', 45455)
CHRM_SRGB = struct.pack("!8I", 31270, 32900, 64000, 33000, 30000, 60000, 15000, 6000)


SRGB_PNGINFO = PngInfo()
SRGB_PNGINFO.add(b"gAMA", GAMA_SRGB)
SRGB_PNGINFO.add(b"cHRM", CHRM_SRGB)


def putchunk_srgb(fp, cid, *data):
    if cid == b"iCCP":
        return putchunk(fp, b'sRGB', b'\3')

    return putchunk(fp, cid, *data)


def save_srgb_png(im, fp, filename, chunk=putchunk_srgb, check=_EMPTY):
    if check is _EMPTY:
        return _save(im, fp, filename, chunk)
    return _save(im, fp, filename, chunk, check)


register_save(FORMAT_NAME, save_srgb_png)


def srgb() -> dict:
    return {
        "format": FORMAT_NAME,
        "icc_profile": b"\0",
        "pnginfo": SRGB_PNGINFO
    }

class ClipDisplay:
    zlib_compression=1

    def __init__(self, clip):
        self.clip = clip

    async def render(self, size: Size, planes, format: RawFormat) -> bytes:
        planes = [
            frombuffer('L', (size.width, size.height), plane, "raw", "L",  format.get_stride(idx, size), 1)
            for idx, plane in enumerate(planes)
        ]

        if len(planes) == 4:
            img = merge("RGBA", planes)
        else:
            img = merge("RGB", planes)

        f = io.BytesIO()
        img.save(f, compress_level=1, **srgb())
        return f.getvalue()

    async def display(self):
        async with self.clip:
            async with self.clip[0] as frame:
                native_format = frame.native_format
                if native_format.alpha:
                    target = RGBA32
                    if not await frame.can_render(RGBA32):
                        target = RGB24
                else:
                    target = RGB24
                    if not await frame.can_render(RGB24):
                        target = RGBA32
                
                if not await frame.can_render(target):
                    return None

                size = frame.size
                
                buffers = [bytearray(target.get_plane_size(idx, size)) for idx in range(target.num_planes)]

                await asyncio.gather(*(
                    frame.render_into(buffers[idx], idx, target)
                    for idx, buffer in enumerate(buffers))
                )
        
        return await self.render(size, [bytes(buffer) for buffer in buffers], target)