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
from yuuno2.networking.connection import Handler, MessageBus, Connection
from yuuno2.networking.message import Message

from aiounittest import AsyncTestCase


class TestCallbackHandler(AsyncTestCase):

    async def test_register_emit(self):
        handler = Handler()
        called = None
        async def _emit(v):
            nonlocal called
            called = v
        
        async with handler:
            await handler.create(_emit)
            await handler.emit(1)
            self.assertEqual(called, 1)
    
    async def test_register_emit_sync(self):
        handler = Handler()
        called = None
        def _emit(v):
            nonlocal called
            called = v
        
        async with handler:
            await handler.create(_emit)
            await handler.emit(1)
            self.assertEqual(called, 1)

    async def test_register_emit_multi(self):
        handler = Handler()
        called1 = None
        def _emit1(v):
            nonlocal called1
            called1 = v

        called2 = None
        def _emit2(v):
            nonlocal called2
            called2 = v

        async with handler:
            await handler.create(_emit1)
            await handler.create(_emit2)
            await handler.emit(1)
            self.assertEqual(called1, 1)
            self.assertEqual(called2, 1)

    async def test_register_unregister(self):
        handler = Handler()

        called1 = None
        def _emit1(v):
            nonlocal called1
            called1 = v

        called2 = None
        def _emit2(v):
            nonlocal called2
            called2 = v
        
        async with handler:
            c = await handler.create(_emit1)
            await handler.create(_emit2)

            await handler.emit(1)
            self.assertEqual(called1, 1)
            self.assertEqual(called2, 1)

            await c.release()

            await handler.emit(2)
            self.assertEqual(called1, 1)
            self.assertEqual(called2, 2)


class TestMessageBus(AsyncTestCase):

    async def test_message_bus_register(self):
        called = None
        def _emit(v):
            nonlocal called
            called = v

        bus = MessageBus()
        async with bus:
            await bus.on_message(_emit)
            await bus.send(Message({"id": id(self)}))
            self.assertEqual(called, Message({"id": id(self)}))

    async def test_message_bus_unregister(self):
        called1 = None
        def _emit1(v):
            nonlocal called1
            called1 = v

        called2 = None
        def _emit2(v):
            nonlocal called2
            called2 = v

        bus = MessageBus()
        async with bus:
            c = await bus.on_message(_emit1)
            await bus.on_message(_emit2)

            await bus.send(Message({"id": id(self), "call": 1}))

            self.assertEqual(called1, Message({"id": id(self), "call": 1}))
            self.assertEqual(called2, Message({"id": id(self), "call": 1}))

            await c.release()
    

class TestConnection(AsyncTestCase):

    async def test_connection_receive(self):
        called1 = None
        def _emit1(v):
            nonlocal called1
            called1 = v

        called2 = None
        def _emit2(v):
            nonlocal called2
            called2 = v

        mb1 = MessageBus()
        mb2 = MessageBus()

        conn = Connection(mb1, mb2)
        async with conn:
            c = await conn.on_message(_emit1)
            await mb1.on_message(_emit2)

            await mb1.send(Message({"id": id(self), "call": 1}))
            self.assertEqual(called1, Message({"id": id(self), "call": 1}))
            self.assertEqual(called2, Message({"id": id(self), "call": 1}))

            await c.release()

            await mb1.send(Message({"id": id(self), "call": 2}))
            self.assertEqual(called1, Message({"id": id(self), "call": 1}))
            self.assertEqual(called2, Message({"id": id(self), "call": 2}))

    
    async def test_connection_unrelease(self):
        called1 = None
        def _emit1(v):
            nonlocal called1
            called1 = v

        called2 = None
        def _emit2(v):
            nonlocal called2
            called2 = v

        mb1 = MessageBus()
        mb2 = MessageBus()

        conn = Connection(mb1, mb2)
        async with mb1: 
            await mb1.on_message(_emit2)

            async with conn:
                await conn.on_message(_emit1)

                await mb1.send(Message({"id": id(self), "call": 1}))
                self.assertEqual(called1, Message({"id": id(self), "call": 1}))
                self.assertEqual(called2, Message({"id": id(self), "call": 1}))

            await mb1.send(Message({"id": id(self), "call": 2}))
            self.assertEqual(called1, Message({"id": id(self), "call": 1}))
            self.assertEqual(called2, Message({"id": id(self), "call": 2}))
        
    
    async def test_connection_send(self):
        called = None
        def _emit(v):
            nonlocal called
            called = v

        mb1 = MessageBus()
        mb2 = MessageBus()

        conn = Connection(mb1, mb2)
        async with mb2:
            await mb2.on_message(_emit)

            async with conn:
                await conn.send(Message({"id": id(self), "call": 1}))
                self.assertEqual(called, Message({"id": id(self), "call": 1}))
