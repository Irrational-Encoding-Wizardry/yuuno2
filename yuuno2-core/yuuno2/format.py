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
from enum import IntEnum, Enum
from typing import NamedTuple, Optional, List, Tuple


class Size(NamedTuple):
    width: int
    height: int


class SampleType(IntEnum):
    INTEGER = 0
    FLOAT = 1


class ColorFamily(Enum):
    GREY = (0, 1, "grey", ["g"])
    RGB  = (1, 3, "rgb",  ["r", "g", "b"])
    YUV  = (2, 3, "yuv",  ["y", "u", "v"])
    CMYK = (3, 4, "cmyk", ["c", "m", "y", "k"])

    def __init__(self, v1num: int, planes: int, name: str, simple_fields: List[str]):
        self.v1num = v1num
        self.planes = planes
        self.name = name
        self.simple_fields = simple_fields


class RawFormat(NamedTuple):
    family: ColorFamily
    fields: List[Optional[str]]
    alpha: bool

    sample_type: SampleType
    bits_per_sample: int
    _alignment: int = 0

    planar: bool = True
    subsampling: Tuple[int, int] = [0, 0]

    def __init__(self, *args, **kwargs):
        if "alignment" in kwargs:
            kwargs["_alignment"] = kwargs.pop("alignment", 0)
        super().__init__(*args, **kwargs)

    @classmethod
    def from_json(self, data):
        if data[-1] == "v1":
            cf = [ColorFamily.GREY, ColorFamily.RGB, ColorFamily.YUV][data[2]]
            st = SampleType(data[3])
            bpp = data[0]

            if data[6]:
                alignment = 4
            else:
                alignment = (bpp + 7) // 8

            halpha = cf.planes+1 == data[1]
            fields = cf.simple_fields[:]
            if halpha:
                fields.append("a")
            elif data[6]:
                fields.append(None)

            data = [{
                "colorspace": {
                    "family": cf.name,
                    "alpha": halpha,
                    "fields": fields
                },
                "dataformat": {
                    "type": "float" if st == SampleType.FLOAT else "integer",
                    "size": bpp
                },
                "planar": data[7],
                "subsampling": [
                    data[5],
                    data[4]
                ],
                "alignment": alignment
            }, "v2"]

        if data[-1] == "v2":
            info = data[0]
            cf = ColorFamily[info["colorspace"]["family"]]
            alpha = info["colorspace"]["alpha"]
            fields = info["colorspace"]["fields"]

            st = SampleType[info["dataformat"]["type"].upper()]
            sz = info["dataformat"]["size"]

            planar = info["planar"]
            subsampling = info["subsampling"]
            alignment = info["alignment"]

            return RawFormat(cf, fields, alpha, st, sz, alignment, planar, subsampling)

        raise ValueError("Unsupported format")

    def to_json(self):
        return [{
            "colorspace": {
                "family": self.family.name,
                "alpha": self.alpha,
                "fields": self.fields
            },
            "dataformat": {
                "type": "float" if self.sample_type == SampleType.FLOAT else "integer",
                "size": self.bits_per_sample
            },
            "planar": self.planar,
            "subsampling": self.subsampling,
            "alignment": self.alignment
        }, "v2"]

    def replace(self, **settings) -> 'RawFormat':
        return self._replace(**settings)

    @property
    def bytes_per_sample(self) -> int:
        return (self.bits_per_sample + 7) // 8

    @property
    def num_fields(self) -> int:
        return self.family.simple_fields + self.alpha

    @property
    def num_planes(self) -> int:
        if self.planar:
            return self.num_fields
        else:
            return 1

    @property
    def alignment(self):
        if self._alignment == 0:
            if self.planar:
                return self.bytes_per_sample
            else:
                return self.bytes_per_sample * self.num_fields
        return self._alignment

    def get_stride(self, plane: int, size: Size) -> int:
        stride = self.get_plane_dimensions(plane, size).width

        if not self.planar:
            stride *= self.num_fields

        alignment = self.alignment
        if stride % alignment != 0:
            stride += (alignment - (stride % alignment))

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
            w >>= self.subsampling[0]
            h >>= self.subsampling[1]
        return Size(w, h)

    def get_plane_size(self, plane: int, size: Size) -> int:
        """
        Calcute the size of the plane in bytes.

        :param plane:  The index of the plane.
        :param size:   The size of the frame (on plane 0)
        """
        stride = self.get_stride(plane, size)
        return size.height * stride


RawFormat.SampleType = SampleType
RawFormat.ColorFamily = ColorFamily

#                  Families          Field-Order            Alpha  Sample-Type       BPP Alignment Planar  Subsampling
GRAY8  = RawFormat(ColorFamily.GREY, ["g"],                 False, SampleType.INTEGER, 8, 1,       True,   (0, 0))
RGB24  = RawFormat(ColorFamily.RGB,  ["r", "g", "b"],       False, SampleType.INTEGER, 8, 1,       True,   (0, 0))
RGBX32 = RawFormat(ColorFamily.RGB,  ["r", "g", "b", None], False, SampleType.INTEGER, 8, 4,       False,  (0, 0))
RGBA32 = RawFormat(ColorFamily.RGB,  ["r", "g", "b", "a"],  True,  SampleType.INTEGER, 8, 4,       False,  (0, 0))
