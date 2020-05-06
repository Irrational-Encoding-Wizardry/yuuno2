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
from yuuno2.networking.connection import Handler, MessageBus, Connection, pipe
from yuuno2.networking.message import Message
from yuuno2.networking.rpc import Server, Client, make_client_server_on, RPCCallFailed

from yuuno2.asyncutils import register_event_loop, clear_event_loop

from yuuno2.tests.utils import with_registered_yuuno

import asyncio
from functools import wraps
from aiounittest import AsyncTestCase



class StatTestObject:

    def __init__(self):
        self.last_call = None

    def on_call_sync(self, id):
        self.last_call = id
        return Message({"id": id})

    async def on_call(self, id):
        self.last_call = id
        return Message({"id": id})

    async def on_fail(self, id):
        raise RuntimeError(f"fail-id({id})")


class DynTestObj:

    def __init__(self, v):
        self.v = v

    def on_invoke(self, **params):
        values = {}
        values.update(params)
        values.update(self.v)
        return Message(values)


class TestServer(AsyncTestCase):

    @with_registered_yuuno
    async def test_server_answer_synchronous(self):
        last_receive = None
        def _recv(message):
            nonlocal last_receive
            last_receive = message

        target = StatTestObject()

        mb1 = MessageBus()
        mb2 = MessageBus()

        connection = Connection(mb1, mb2)
        srv = Server(connection)

        async with srv:
            await mb2.on_message(_recv)
            await srv.register("test", target)
            await mb1.send(Message({"id": 1, "type": "invoke", "target": "test", "method": "call_sync", "payload": {"id": id(self)}}))
            await asyncio.sleep(0.5)
            self.assertEqual(last_receive, Message({"id": 1, "type": "result", "payload": {"id": id(self)}}))
            self.assertEqual(target.last_call, id(self))

    @with_registered_yuuno
    async def test_server_answer_asynchronous(self):
        last_receive = None
        def _recv(message):
            nonlocal last_receive
            last_receive = message

        target = StatTestObject()

        mb1 = MessageBus()
        mb2 = MessageBus()

        connection = Connection(mb1, mb2)
        srv = Server(connection)

        async with srv:
            await mb2.on_message(_recv)
            await srv.register("test", target)
            await mb1.send(Message({"id": 1, "type": "invoke", "target": "test", "method": "call", "payload": {"id": id(self)}}))
            await asyncio.sleep(0.5)
            self.assertEqual(last_receive, Message({"id": 1, "type": "result", "payload": {"id": id(self)}}))
            self.assertEqual(target.last_call, id(self))

    @with_registered_yuuno
    async def test_server_answer_fail(self):
        last_receive = None
        def _recv(message):
            nonlocal last_receive
            last_receive = message

        target = StatTestObject()

        mb1 = MessageBus()
        mb2 = MessageBus()

        connection = Connection(mb1, mb2)
        srv = Server(connection)

        async with srv:
            await mb2.on_message(_recv)
            await srv.register("test", target)
            await mb1.send(Message({"id": 1, "type": "invoke", "target": "test", "method": "fail", "payload": {"id": id(self)}}))
            await asyncio.sleep(0.5)
            self.assertTrue(f"fail-id({id(self)})" in last_receive.data["message"])


class TestClient(AsyncTestCase):

    @with_registered_yuuno
    async def test_client_proxy_sync(self):
        target = StatTestObject()

        mb1 = MessageBus()
        mb2 = MessageBus()

        c_srv = Connection(mb1, mb2)
        c_cli = Connection(mb2, mb1)
        srv = Server(c_srv)
        cli = Client(c_cli)
        async with srv, cli:
            await srv.register("test", target)
            proxy = await cli.get("test")
            msg = await asyncio.wait_for(proxy.call(id=id(self)), 5)
            self.assertEqual(msg, Message({"id": id(self)}))

    @with_registered_yuuno
    async def test_client_proxy(self):
        target = StatTestObject()

        mb1 = MessageBus()
        mb2 = MessageBus()

        c_srv = Connection(mb1, mb2)
        c_cli = Connection(mb2, mb1)
        srv = Server(c_srv)
        cli = Client(c_cli)
        async with srv, cli:
            await srv.register("test", target)
            proxy = await cli.get("test")
            try:
                msg = await asyncio.wait_for(proxy.fail(id=id(self)), 5)
            except RPCCallFailed as e:
                self.assertIn(f"fail-id({id(self)})", str(e))


class TestPipedConnection(AsyncTestCase):

    @with_registered_yuuno
    async def test_two_endpoints(self):
        t1, t2 = DynTestObj({"t": 1}), DynTestObj({"t": 2})

        p1, p2 = pipe()
        s1, c1 = make_client_server_on(p1)
        s2, c2 = make_client_server_on(p2)

        async with s1, s2, c1, c2:
            await s1.register("test", t1)
            await s2.register("test", t2)

            x1 = await c1.get("test")
            x2 = await c2.get("test")

            try:
                self.assertEqual(await asyncio.wait_for(x1.invoke(v=0), 5), Message({"t": 2, "v": 0}))
                self.assertEqual(await asyncio.wait_for(x2.invoke(v=1), 5), Message({"t": 1, "v": 1}))
            except RPCCallFailed as e:
                raise
