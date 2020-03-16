#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017-2019 StuxCrystal (Roland Netzsch <stuxcrystal@encode.moe>)
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
import weakref
from asyncio import ensure_future, wrap_future, gather
from typing import NoReturn, Mapping, Union, Optional, Awaitable

import vapoursynth as vs
from vapoursynth import VideoFrame, VideoNode, Format, core

from yuuno2.clips.combined_alpha import AlphaClip
from yuuno2.format import RawFormat, SampleType, ColorFamily, Size
from yuuno2.resource_manager import register
from yuuno2.typings import Buffer, ConfigTypes
from yuuno2.clip import Frame, Clip
from yuuno2.script import Script


ConfigMapping = Mapping[str, ConfigTypes]
_config_cache = weakref.WeakKeyDictionary()
DEFAULT_CONFIGURATION = {
    'chroma_resizer':      'resize.Spline36',
    'override_yuv_matrix': False,
    'default_yuv_matrix':  '702',
}


async def get_configuration(script: Script) -> ConfigMapping:
    config = [[k, ensure_future(script.get_config("vs." + k, d))] for k, d in DEFAULT_CONFIGURATION.items()]
    await gather(*(d for k, d in config))
    return {k: (d.result()) for k, d in config}


def get_frame_async(node: VideoNode, frame: int) -> Awaitable[VideoFrame]:
    sfut = node.get_frame_async(frame)
    return wrap_future(sfut)


def extract_plane(buffer: Buffer, offset: int, frame: VideoFrame, planeno: int):
    """
    Extracts the plane with the VapourSynth R37+ array-API.

    :param buffer:  Target buffer
    :param offset:  Where to write it
    :param frame:   The frame
    :param planeno: The plane number
    :return: The extracted image.
    """
    arr = frame.get_read_array(planeno)
    length = len(arr)

    if length+offset > len(buffer):
        raise BufferError("Buffer too short.")

    buffer[offset:offset+length] = arr

    return len(arr)


FORMAT_COMPATBGR32 = RawFormat(
    ColorFamily.RGB,
    ["b", "g", "r", None],
    False,
    SampleType.INTEGER,
    8,
    4,
    False,
    (0, 0)
)
FORMAT_COMPATYUY2 = RawFormat(
    ColorFamily.YUV,
    ["y", "u", "y", "v"],
    False,
    SampleType.INTEGER,
    8,
    4,
    False,
    (1, 0)
)


class VapourSynthFrame(Frame):
    def __init__(self, script: Script, clip: 'VapourSynthClip', frameno: int):
        register(clip, self)
        self.script = script
        self.clip = clip.clip
        self.frameno = frameno
        self._raw_node: Optional[VideoNode] = None
        self._raw_frame: Optional[VideoFrame] = None

    @property
    def size(self) -> Size:
        if not self.acquired:
            return Size(0, 0)
        return Size(self._raw_frame.width, self._raw_frame.height)

    @property
    def native_format(self) -> RawFormat:
        if not self.acquired:
            return FORMAT_COMPATBGR32

        ff: Format = self._raw_frame.format
        if ff.color_family == vs.COMPAT:
            if int(ff) == vs.COMPATBGR32:
                return FORMAT_COMPATBGR32
            else:
                return FORMAT_COMPATYUY2
        else:
            fam = {
                vs.RGB: ColorFamily.RGB,
                vs.GRAY: ColorFamily.GREY,
                vs.YUV: ColorFamily.YUV,
                vs.YCOCG: ColorFamily.YUV
            }[ff.color_family]

        samples = SampleType.INTEGER if ff.sample_type==vs.INTEGER else SampleType.FLOAT
        return RawFormat(
            sample_type=samples,
            family=fam,
            fields=fam.simple_fields,
            subsampling=(ff.subsampling_w, ff.subsampling_h),
            bits_per_sample=ff.bits_per_sample,
            planar=True,
            alpha=False
        )

    async def can_render(self, format: RawFormat) -> bool:
        await self.ensure_acquired()

        if format == self.native_format:
            return True
        elif not format.planar:
            if format == FORMAT_COMPATBGR32:
                return True
            elif format == FORMAT_COMPATYUY2:
                return True
            else:
                return False
        elif format.alpha:
            return False
        elif format.alignment != format.bytes_per_sample:
            return False
        else:
            return True

    async def render_into(self, buffer: Buffer, plane: int, format: RawFormat, offset: int = 0) -> int:
        if not (await self.can_render(format)):
            raise ValueError("Unsupported format.")

        if not (0 <= plane < format.num_planes):
            raise IndexError(f"Plane index out of range (0 <= {plane} <= {format.num_planes}")

        config = dict(await get_configuration(self.script))
        with self.script.inside():
            _converted = self._convert(format, config)
            _fut = get_frame_async(_converted, 0)
        frame: VideoFrame = await _fut

        # Convert plane indices of planar formats transparently.
        planename = format.fields[plane]
        if planename is None:
            return len(buffer) - offset
        planeidx = format.family.simple_fields.index(planename)

        return extract_plane(buffer, offset, frame, planeidx)

    def _convert(self, format: RawFormat, config) -> VideoNode:
        if format == self.native_format:
            return self._raw_node

        namespace, filter = config['chroma_resizer'].split(".", 2)
        config['chroma_resizer'] = getattr(getattr(core, namespace), filter)

        if not format.planar:
            return self._convert_compat(format, config)
        elif format.family == ColorFamily.RGB:
            return self._convert_rgb(format, config)
        elif format.family == ColorFamily.YUV:
            return self._convert_grey(format, config)
        else:
            return self._convert_grey(format, config)

    def _convert_compat(self, format: RawFormat, config) -> VideoNode:
        if format == FORMAT_COMPATBGR32:
            clip = self._convert_rgb(format, config)
            return config['chroma_resizer'](clip, format=vs.COMPATBGR32)
        else:
            clip = self._convert_yuv(format, config)
            return config['chroma_resizer'](clip, format=vs.COMPATYUY2)

    def _convert_rgb(self, format: RawFormat, config) -> VideoNode:
        target = core.get_format(vs.RGB24).replace(
            bits_per_sample=format.bits_per_sample,
            sample_type=(vs.INTEGER if format.sample_type == SampleType.INTEGER else vs.FLOAT)
        )

        params = {'format': target}
        if self._raw_frame.format.color_family == vs.YUV:
            params.update(
                matrix_in_s  = config['default_yuv_matrix'],
                prefer_props = config['override_yuv_matrix']
            )

        return config['resizer'](self._raw_node, **params)

    def _convert_yuv(self, format: RawFormat, config) -> VideoNode:
        target = core.get_format(vs.YUV444P8).replace(
            bits_per_sample = format.bits_per_sample,
            subsampling_w   = format.subsampling[0],
            subsampling_h   = format.subsampling[1],
            sample_type     = (vs.INTEGER if format.sample_type == SampleType.INTEGER else vs.FLOAT)
        )
        params = {
            'format': target,
        }
        if self._raw_frame.format.color_family not in (vs.YUV, vs.YCOCG):
            params.update(
                matrix_s = config['default_yuv_matrix']
            )

        return config['resizer'](
            self._raw_node,
            **params
        )

    def _convert_grey(self, format: RawFormat, config):
        target = core.get_format(vs.GRAY8).replace(
            bits_per_sample= format.bits_per_sample,
            sample_type    = (vs.INTEGER if format.sample_type == SampleType.INTEGER else vs.FLOAT)
        )
        return config['resizer'](
            self._raw_node,
            format=target,
            matrix_in_s=config['default_yuv_matrix'],
            prefer_props=config['override_yuv_matrix']
        )

    async def get_metadata(self) -> Mapping[str, Union[int, str, bytes]]:
        return self._raw_frame.props

    async def _acquire(self) -> NoReturn:
        with self.script.inside():
            self._raw_node = self.clip[self.frameno]
            _fut = get_frame_async(self._raw_node, 0)

        self._raw_frame = await _fut

    async def _release(self) -> NoReturn:
        self._raw_node = None
        self._raw_frame = None


class _VapourSynthClip(Clip):

    def __init__(self, script: Script, clip: VideoNode):
        register(script, self)
        self.script = script
        self.clip = clip

    def __len__(self):
        return len(self.clip)

    def __getitem__(self, frameno):
        return VapourSynthFrame(self.script, self, frameno)

    async def get_metadata(self) -> Mapping[str, Union[int, str, bytes]]:
        return {}

    async def _acquire(self) -> NoReturn:
        pass

    async def _release(self) -> NoReturn:
        self.clip = None


def VapourSynthClip(clip: Union[vs.VideoNode, vs.AlphaOutputTuple], script: Optional[Script] = None) -> Clip:
    if isinstance(clip, vs.AlphaOutputTuple):
        m, a = clip
        return AlphaClip(
            _VapourSynthClip(script, m),
            _VapourSynthClip(script, a)
        )
    return _VapourSynthClip(script, clip)
