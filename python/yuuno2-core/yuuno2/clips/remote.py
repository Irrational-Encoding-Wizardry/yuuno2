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
from typing import Optional, Union, List, Mapping

from yuuno2.clip import Clip, MetadataContainer, Frame
from yuuno2.format import RawFormat, Size
from yuuno2.networking.base import Connection, Message
from yuuno2.networking.reqresp import ReqRespServer, ReqRespClient, function
from yuuno2.resource_manager import register
from yuuno2.typings import Buffer


class ClipServer(ReqRespServer):

    def __init__(self, clip: Clip, parent: Connection):
        self.clip = clip
        super().__init__(parent)

    async def _acquire(self):
        await super()._acquire()

        await self.clip.acquire()
        register(self.clip, self)

    async def _release(self):
        await self.clip.release(force=False)
        await super()._release()

    async def on_metadata(self, frame: Optional[int] = None) -> Message:
        mc: MetadataContainer = self.clip if frame is None else self.clip[frame]
        async with mc:
            metadata = await mc.get_metadata()
        return Message(metadata, [])

    async def on_length(self) -> Message:
        return Message({'length': len(self.clip)})

    # noinspection PyTypeChecker
    async def on_size(self, frame: int) -> Message:
        frame_inst = self.clip[frame]
        async with frame_inst:
            sz = frame_inst.size
            return Message(
                [sz.width, sz.height]
            )

    async def on_format(self, frame: int) -> Message:
        frame_inst = self.clip[frame]
        async with frame_inst:
            return Message(
                frame_inst.native_format.to_json()
            )

    async def on_render(
            self,
            frame: int,
            format: Optional[list] = None,
            planes: Optional[Union[List[int], int]] = None
    ) -> Message:
        frame_inst = self.clip[frame]
        async with frame_inst:
            if planes is None:
                return Message({'size': list(frame_inst.size)}, [])

            format: RawFormat = RawFormat.from_json(format)
            if not (await frame_inst.can_render(format)):
                return Message({'size': None})

            if not isinstance(planes, (list, tuple)):
                planes: List[int] = [planes]

            buffers = [
                bytearray(format.get_plane_size(p, frame_inst.size))
                for p in planes
            ]
            used_buffers = await gather(*(
                frame_inst.render_into(buf, p, format, 0)
                for p, buf in enumerate(buffers)
            ))
            return Message(
                {'size': list(frame_inst.size)},
                [buf[:sz] for buf, sz in zip(buffers, used_buffers)]
            )


class ClipClient(ReqRespClient):
    render = function()
    metadata = function()

    size = function()
    format = function()
    length = function()


class RemoteFrame(Frame):

    def __init__(self, frame: int, clip: 'RemoteClip', client: ClipClient):
        self.frame = frame
        self.remote_clip = clip
        self.client = client

        self._native_format = None
        self._size = None

    async def _acquire(self) -> None:
        await self.remote_clip.acquire()
        await self.client.acquire()

        register(self.remote_clip, self)
        register(self.client, self)

        msg_sz, msg_format = await gather(
            self.client.size(frame=self.frame),
            self.client.format(frame=self.frame)
        )
        self._size = Size(*msg_sz.values)
        self._native_format = RawFormat.from_json(msg_format.values)

    async def _release(self) -> None:
        await self.remote_clip.release(force=False)
        await self.client.release(force=False)
        self.remote_clip = None
        self.client = None

    @property
    def native_format(self) -> RawFormat:
        return self._native_format

    @property
    def size(self) -> Size:
        return self._size

    async def can_render(self, format: RawFormat) -> bool:
        await self.ensure_acquired()

        f_json = format.to_json()
        response: Message = await self.client.render(
            frame=self.frame,
            format=f_json,
            planes=[]
        )
        return response.values['size'] is not None

    async def render_into(self, buffer: Buffer, plane: int, format: RawFormat, offset: int = 0) -> int:
        await self.ensure_acquired()

        f_json = format.to_json()
        response: Message = await self.client.render(
            frame=self.frame,
            format=f_json,
            planes=[plane]
        )
        if response.values['size'] is None:
            raise ValueError("Unsupported format.")

        buf_sz = len(response.blobs[0])
        buffer[:buf_sz] = response.blobs[0]
        return buf_sz

    async def get_metadata(self) -> Mapping[str, Union[int, str, bytes]]:
        await self.ensure_acquired()

        response: Message = await self.client.metadata(
            frame=self.frame
        )
        return response.values


class RemoteClip(Clip):
    def __init__(self, connection: Connection):
        self.connection = connection
        self._client = None
        self._sz = None

    def __getitem__(self, item) -> Frame:
        if 0 > item or item >= len(self):
            raise IndexError("Clip index out of range.")

        return RemoteFrame(item, self, self._client)

    def __len__(self):
        if not self.acquired:
            raise RuntimeError("Clip not acquired.")
        return self._sz

    async def _acquire(self) -> None:
        await self.connection.acquire()
        register(self.connection, self)

        self._client = ClipClient(self.connection)
        await self._client.acquire()
        register(self, self._client)

        msg: Message = await self._client.length()
        self._sz = msg.values['length']

    async def _release(self) -> None:
        await self.connection.release(force=False)

    async def get_metadata(self) -> Mapping[str, Union[int, str, bytes]]:
        await self.ensure_acquired()
        msg: Message = await self._client.metadata()
        return msg.values
