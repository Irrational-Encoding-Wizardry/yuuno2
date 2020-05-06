#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2020 StuxCrystal (Roland Netzsch <stuxcrystal@encode.moe>)
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
import uuid
import asyncio
from typing import Optional

from yuuno2.clip import Clip, Frame
from yuuno2.format import RawFormat, Size
from yuuno2.resource_manager import Resource, register

from yuuno2.networking.message import Message
from yuuno2.networking.rpc import Server, Client, RPCProxy
from yuuno2.networking.connection import BaseConnection
from yuuno2.networking.manager import RemoteManager


class ClipWrapper(Resource):

    def __init__(self, clip: Clip):
        self.clip = clip

    async def on_length(self) -> Message:
        await self.ensure_acquired()
        return Message({"length": len(self.clip)})

    async def on_format(self, frameno: int) -> Message:
        await self.ensure_acquired()
        async with self.clip[frameno] as frame:
            return Message({
                "format": frame.native_format.to_json()
            })

    async def on_size(self, frameno: int) -> Message:
        await self.ensure_acquired()
        async with self.clip[frameno] as frame:
            return Message({
                "width": frame.size.width,
                "height": frame.size.height
            })

    async def on_metadata(self, frameno: int=None):
        await self.ensure_acquired()
        if frameno is None:
            return Message({
                "metadata": await self.clip.get_metadata()
            })
        else:
            async with self.clip[frameno] as frame:
                return Message({
                    "metadata": await frame.get_metadata()
                })

    async def on_can_render(self, frameno: int, format, size=None) -> Message:
        await self.ensure_acquired()

        clip = self.clip
        if size is not None:
            clip = await clip.resize(Size(size["width"], size["height"]))

        async with clip:
            format = RawFormat.from_json(format)
            async with clip[frameno] as frame:
                return Message({
                    "supported": await frame.can_render(format)
                })

    async def on_render(self, frameno: int, planes, format=None, size=None) -> Message:
        await self.ensure_acquired()

        clip = self.clip
        if size is not None:
            clip = await clip.resize(Size(size["width"], size["height"]))

        async with clip:
            if format is not None:
                format = RawFormat.from_json(format)
            else:
                format = clip.native_format

            if isinstance(planes, int):
                planes = [planes]

            async with clip[frameno] as frame:
                if not await frame.can_render(format):
                    return Message({
                        "success": False
                    })
                planes = [bytearray(format.get_plane_size(plane, frame.size)) for plane in planes]
                await asyncio.gather(*(frame.render_into(plane, idx, format) for plane, idx in enumerate(planes)))
                return Message({
                    "success": True
                }, planes)

    async def _acquire(self):
        await self.clip.acquire()
        register(self.clip, self)

    async def _release(self):
        await self.clip.release(force=False)

    @classmethod
    async def on_manager(cls, clip: Clip, manager: Server, *, name: Optional[str]=None) -> 'ClipWrapper':
        if name is None:
            name = str(uuid.uuid4())

        wrapper = cls(clip)

        registration = manager.register(name, wrapper)
        register(wrapper, registration)

        return wrapper


class RemoteFrame(Frame):

    def __init__(self, rpc: RPCProxy, frameno: int, size: Optional[Size]=None):
        self.rpc = rpc
        self.frameno = frameno
        self._resized_sz = size
        self.__size = size
        self.__format = format
    
    @property
    def size(self) -> Size:
        self.ensure_acquired_sync()
        if self._resized_sz is not None:
            return self._resized_sz
        return self.__size

    @property
    def native_format(self) -> RawFormat:
        self.ensure_acquired_sync()
        return self.__format

    @property
    def _resized_sz_json(self):
        if self._resized_sz is None:
            return None
        return {
            "width": self._resized_sz.width,
            "height": self._resized_sz.height
        }

    async def get_metadata(self):
        await self.ensure_acquired()
        msg = await self.rpc.metadata(frameno=None)
        return msg.data["metadata"]

    async def can_render(self, format):
        await self.ensure_acquired()
        msg = await self.rpc.can_render(frameno=self.frameno, format=format.to_json, size=self._resized_sz_json)
        return msg.data["supported"]

    async def render_into(self, buffer, plane, format, offset=0) -> int:
        rendered = await self.rpc.render(self.frameno, planes=[plane], format=format.to_json, size=self._resized_sz_json)
        if not rendered.data["success"]:
            raise ValueError("Failed to render.")
        length = rendered.blobs[0]
        if len(length) > len(buffer)+offset:
            raise BufferError("Buffer not large enough.")
        buffer[offset:length+offset] = rendered.blobs[0]
        return length

    async def _acquire(self):
        await self.rpc.acquire()
        register(self.rpc, self)

        size, format = await asyncio.gather(self.rpc.size(frameno=self.frameno), self.rpc.format(frameno=self.frameno))
        self.__size = Size(width=size.data["width"], height=size.data["height"])
        self.__format = RawFormat.from_json(format.data["format"])

    async def _release(self):
        await self.rpc.release(force=False)


class RemoteClip(Clip):

    def __init__(self, rpc: RPCProxy, size: Optional[Size] = None):
        self.rpc = rpc
        self.size = size

        self.__length = None

    def __len__(self):
        self.ensure_acquired_sync()
        return self.__length

    def __getitem__(self, frameno):
        self.ensure_acquired_sync()
        return RemoteFrame(self.rpc, frameno, self.size)
    
    async def get_metadata(self):
        await self.ensure_acquired()
        msg = await self.rpc.metadata(frameno=None)
        return msg.data["metadata"]

    async def resize(self, size: Size):
        return RemoteClip(rpc, size)

    async def _acquire(self):
        await self.rpc.acquire()
        register(self.rpc, self)

        msg: Message = await self.rpc.length()
        self.__length = msg.data["length"]

    async def _release(self):
        await self.rpc.release(force=False)

    @classmethod
    async def from_client(cls, client: Client, name: str):
        clip = cls(await client.get(name))
        register(client, clip)
        return clip

    @classmethod
    async def from_manager(cls, manager: RemoteManager, name: str):
        clip = cls(await manager.get(name))
        register(manager, clip)
        return clip