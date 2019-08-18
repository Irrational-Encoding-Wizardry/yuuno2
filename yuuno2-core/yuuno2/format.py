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
from enum import IntEnum
from typing import NamedTuple


class Size(NamedTuple):
    width: int
    height: int


class SampleType(IntEnum):
    INTEGER = 0
    FLOAT = 1


class ColorFamily(IntEnum):
    GREY = 0
    RGB = 1
    YUV = 2


class RawFormat(NamedTuple):
    bits_per_sample: int
    num_fields: int
    family: ColorFamily
    sample_type: SampleType
    subsampling_h: int = 0
    subsampling_w: int = 0
    packed: bool = True
    planar: bool = True

    @classmethod
    def from_json(self, data):
        if data[-1] == "v1":
            data = list(data)
            data[2] = ColorFamily(data[2])
            data[3] = SampleType(data[3])
            return RawFormat(*data[:-1])
        raise ValueError("Unsupported format")

    def to_json(self):
        return (*self, "v1")

    def replace(self, **settings) -> 'RawFormat':
        return self._replace(**settings)


    @property
    def bytes_per_sample(self) -> int:
        # This is faster than
        # int(ceil(bpp/8))
        # and faster than (l,m=divmod(bpp,8); l+bool(m))
        bpp = self.bits_per_sample
        return (bpp // 8) + (bpp % 8 != 0)

    @property
    def num_planes(self) -> int:
        if self.planar:
            return self.num_fields
        else:
            return 1

    def get_stride(self, plane: int, size: Size) -> int:
        stride = self.get_plane_dimensions(plane, size).width
        if not self.packed:
            stride += stride % 4
        return stride

    def get_plane_dimensions(self, plane: int, size: Size) -> Size:
        """
        Returns the size of the plane's picture dimensions.

        :param plane: The plane number.
        :param size:  The size of the plane.
        :return: A new size object with the desired size.
        """
        if not self.planar:
            return size

        w, h = size
        if 0 < plane < 4:
            w >>= self.subsampling_w
            h >>= self.subsampling_h
        return Size(w, h)

    def get_plane_size(self, plane: int, size: Size) -> int:
        """
        Calcute the size of the plane in bytes.

        :param plane:  The index of the plane.
        :param size:   The size of the frame (on plane 0)
        """
        if not self.planar:
            return self.bytes_per_sample * self.num_fields * size.width * size.height

        w, h = self.get_plane_dimensions(plane, size)

        stride = w * self.bytes_per_sample
        if not self.packed:
            stride += stride % 4

        return h * stride


RawFormat.SampleType = SampleType
RawFormat.ColorFamily = ColorFamily

GRAY8 = RawFormat(8, 1, RawFormat.ColorFamily.GREY, RawFormat.SampleType.INTEGER)
RGB24 = RawFormat(8, 3, RawFormat.ColorFamily.RGB, RawFormat.SampleType.INTEGER)
RGBA32 = RawFormat(8, 4, RawFormat.ColorFamily.RGB, RawFormat.SampleType.INTEGER)

