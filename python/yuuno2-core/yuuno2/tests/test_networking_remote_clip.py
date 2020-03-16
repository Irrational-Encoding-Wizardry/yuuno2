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
from asyncio import wait_for

from aiounittest import AsyncTestCase

from yuuno2.clips.remote import ClipServer, RemoteClip
from yuuno2.format import GRAY8, RGB24
from yuuno2.networking.pipe import pipe_bidi
from yuuno2.tests.mocks import MockClip, MockFrame
from yuuno2.tests.utils import timeout_context


class SingleFrameMockClip(MockClip):

    def __init__(self, frame: MockFrame):
        self.frame = frame

    def __getitem__(self, item):
        return self.frame


class RemoteClipTest(AsyncTestCase):

    async def test_clip_metadata_transmit(self):
        c_client, c_server = pipe_bidi()
        mock_clip = MockClip()
        async with mock_clip:
            server = ClipServer(mock_clip, c_server)
            client = RemoteClip(c_client)

            # Make sure the server is acquired first, as otherwise
            # there will be a deadlock.
            async with server, client:
                self.assertEqual(await wait_for(client.get_metadata(), 5), {"id": id(mock_clip)})

    async def test_clip_length(self):
        c_client, c_server = pipe_bidi()
        mock_clip = MockClip()
        async with mock_clip:
            server = ClipServer(mock_clip, c_server)
            client = RemoteClip(c_client)

            # Make sure the server is acquired first, as otherwise
            # there will be a deadlock.
            async with server, client:
                self.assertEqual(len(client), len(mock_clip))

    async def test_clip_frame_metadata(self):
        c_client, c_server = pipe_bidi()
        mock_frame = MockFrame()
        mock_clip = SingleFrameMockClip(mock_frame)
        async with mock_clip, mock_frame:
            server = ClipServer(mock_clip, c_server)
            client = RemoteClip(c_client)

            # Make sure the server is acquired first, as otherwise
            # there will be a deadlock.
            async with timeout_context(server, 10), timeout_context(client, 10):
                remote_frame = client[0]
                async with remote_frame:
                    metadata = await wait_for(remote_frame.get_metadata(), 5)
                    self.assertEqual(metadata, {"id": id(mock_frame)})

    async def test_clip_frame_native_format(self):
        c_client, c_server = pipe_bidi()
        mock_frame = MockFrame()
        mock_clip = SingleFrameMockClip(mock_frame)
        async with mock_clip, mock_frame:
            server = ClipServer(mock_clip, c_server)
            client = RemoteClip(c_client)

            # Make sure the server is acquired first, as otherwise
            # there will be a deadlock.
            async with timeout_context(server, 10), timeout_context(client, 10):
                remote_frame = client[0]
                async with remote_frame:
                    self.assertEqual(remote_frame.native_format, mock_frame.native_format)

    async def test_clip_frame_size(self):
        c_client, c_server = pipe_bidi()
        mock_frame = MockFrame()
        mock_clip = SingleFrameMockClip(mock_frame)
        async with mock_clip, mock_frame:
            server = ClipServer(mock_clip, c_server)
            client = RemoteClip(c_client)

            # Make sure the server is acquired first, as otherwise
            # there will be a deadlock.
            async with timeout_context(server, 10), timeout_context(client, 10):
                remote_frame = client[0]
                async with remote_frame:
                    self.assertEqual(remote_frame.size, mock_frame.size)

    async def test_clip_frame_can_render(self):
        c_client, c_server = pipe_bidi()
        mock_clip = MockClip()
        async with mock_clip:
            server = ClipServer(mock_clip, c_server)
            client = RemoteClip(c_client)

            # Make sure the server is acquired first, as otherwise
            # there will be a deadlock.
            async with timeout_context(server, 10), timeout_context(client, 10):
                remote_frame = client[0]
                async with remote_frame:
                    self.assertFalse(await remote_frame.can_render(GRAY8))
                    self.assertTrue(await remote_frame.can_render(RGB24))

    async def test_clip_frame_render(self):
        c_client, c_server = pipe_bidi()
        mock_clip = MockClip()
        async with mock_clip:
            server = ClipServer(mock_clip, c_server)
            client = RemoteClip(c_client)

            # Make sure the server is acquired first, as otherwise
            # there will be a deadlock.
            async with timeout_context(server, 10), timeout_context(client, 10):
                remote_frame = client[0]
                async with remote_frame:
                    data = bytearray(remote_frame.native_format.get_plane_size(0, remote_frame.size))
                    self.assertEqual(await remote_frame.render_into(data, 0, remote_frame.native_format, 0), 0)

