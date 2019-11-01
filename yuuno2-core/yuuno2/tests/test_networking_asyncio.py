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
import socket
from asyncio import get_running_loop, open_connection, wait_for, sleep

from aiounittest import AsyncTestCase

from yuuno2.networking.asyncio import YuunoProtocol, ConnectionInputStream, ConnectionOutputStream
from yuuno2.networking.base import Message
from yuuno2.networking.serializer import ByteOutputStream


class FakeClosable:
    close = lambda self: None


class TestAsyncioProtocol(AsyncTestCase):

    async def test_read_stream(self):
        rsock, wsock = socket.socketpair()
        rt = None

        try:
            loop = get_running_loop()
            rt, proto = await loop.create_connection(YuunoProtocol, sock=rsock)
            stream = ConnectionInputStream(proto)

            wsock.sendall(ByteOutputStream.write_message(Message({"test": id(self)}, [])))

            async with stream:
                msg = await wait_for(stream.read(), 5)
                self.assertEqual(msg, Message({"test": id(self)}, []))

                wsock.shutdown(socket.SHUT_RDWR)
                await wait_for(stream.read(), 5)
                self.assertFalse(stream.acquired)

        finally:
            if rt is not None:
                rt.close()
            wsock.close()

    async def test_write_stream(self):
        rsock, wsock = socket.socketpair()
        wt = FakeClosable()
        rs_w = FakeClosable()

        try:
            rs_r, rs_w = await open_connection(sock=rsock)
            wt, wp = await get_running_loop().create_connection(YuunoProtocol, sock=wsock)

            wpos = ConnectionOutputStream(wp)
            async with wpos:
                msg = Message({"test": id(self)}, [])
                msg_raw = ByteOutputStream.write_message(msg)
                plength = len(msg_raw)

                await wait_for(wpos.write(msg), 5)
                data = await wait_for(rs_r.readexactly(plength), 5)
                self.assertEqual(data, msg_raw)

            await wait_for(rs_r.read(1), 5)
            self.assertTrue(rs_r.at_eof())

        finally:
            rs_w.close()
            wt.close()

        # Make sure the stream-reader had time get properly closed.
        await sleep(0.1)
