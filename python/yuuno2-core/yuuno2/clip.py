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
from abc import abstractmethod, ABC
from typing import Mapping, Union

from yuuno2.typings import Buffer
from yuuno2.format import Size, RawFormat, RGB24
from yuuno2.resource_manager import Resource


class MetadataContainer(ABC):

    @abstractmethod
    async def get_metadata(self) -> Mapping[str, Union[int, str, bytes]]:
        """
        Returns generic metadata about the frame.

        :return: A mapping of generic metadata.
        """
        return {}


class Frame(MetadataContainer, Resource, ABC):
    """
    This class represents a single frame out of a clip.

    A frame has two properties that can be accessed synchronously:

    1. It's size.
    2. It's metadata.
    """

    @property
    def native_format(self) -> RawFormat:
        """
        Returns the native format of the image.

        This format is guaranteed to be supported by the :func:`render`

        :return: A :class:`yuuno2.format.RawFormat`-instance.
        """
        return RGB24

    @property
    def size(self) -> Size:
        """
        Returns the size of the frame with no subsampling applied.

        :return: A size-object that returns the size of the frame.
        """
        return Size(0, 0)

    @abstractmethod
    async def can_render(self, format: RawFormat) -> bool:
        """
        Checks if the contents of the frame can be rendered in the given format.

        :param format: The format of the frame.
        :return: The native format of the frame.
        """
        return format == self.native_format

    @abstractmethod
    async def render_into(self, buffer: Buffer, plane: int, format: RawFormat, offset: int = 0) -> int:
        """
        Renders the plane of the frame into the given binary buffer.

        :param buffer: The buffer to render the image into.
        :param plane:  The plane to render.
        :param format: The format to render the frame in.
        :param offset: Where in the buffer should you start.

        :exception ValueError:   Thrown if the image cannot be converted to the given format.
        :exception IndexError:   Thrown if the requested plane is outside the plane range.
        :exception BufferError:  Thrown if the buffer is too small at the given offset.

        :return: The amount of bytes written to the binary buffer.
        """
        return 0


class Clip(Resource, MetadataContainer, ABC):
    """
    This class is the base-class for a clip.
    """

    def __len__(self) -> int:
        return 0

    def __getitem__(self, item) -> Frame:
        raise NotImplementedError