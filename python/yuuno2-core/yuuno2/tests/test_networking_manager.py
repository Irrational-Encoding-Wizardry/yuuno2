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
import asyncio
from functools import wraps

from aiounittest import AsyncTestCase

from yuuno2.tests.utils import timeout_context, force_release
from yuuno2.tests.utils import with_registered_yuuno
from yuuno2.asyncutils import register_event_loop, clear_event_loop
from yuuno2.resource_manager import Resource
from yuuno2.networking.message import Message
from yuuno2.networking.connection import pipe
from yuuno2.networking.rpc import Server, Client, RPCCallFailed
from yuuno2.networking.manager import make_managed_connection, RemoteManager, ObjectManager


class DynTestObj(Resource):

    def __init__(self, v):
        self.v = v

    def on_invoke(self, **params):
        values = {}
        values.update(params)
        values.update(self.v)
        return Message(values)

    async def _release(self):
        pass

    async def _acquire(self):
        pass


class TestManager(AsyncTestCase):

    @with_registered_yuuno
    async def test_temporary_object(self):
        s1, s2 = pipe()
        local = ObjectManager(Server(s1))
        remote = RemoteManager(Client(s2))

        obj = DynTestObj({"x": id(self)%2000})

        async with local, remote:
            oid = await asyncio.wait_for(local.add_temporary_object(obj), 5)
            self.assertFalse(obj.acquired)
            self.assertFalse(obj.resource_state.released)

            proxied = await asyncio.wait_for(remote.get(oid), 5)
            self.assertFalse(obj.acquired)
            self.assertFalse(obj.resource_state.released)

            async with timeout_context(proxied, 5):
                self.assertTrue(obj.acquired)
                self.assertFalse(obj.resource_state.released)

                result = await asyncio.wait_for(proxied.invoke(test=id(self)), 5)
                self.assertEqual(result.data, {"x": id(self)%2000, "test": id(self)})

            self.assertFalse(obj.acquired)
            self.assertTrue(obj.resource_state.released)

    @with_registered_yuuno
    async def test_temporary_registration(self):
        s1, s2 = pipe()
        local = ObjectManager(Server(s1))

        cli = Client(s2)
        remote = RemoteManager(cli)

        obj = DynTestObj({"x": id(self)%2000})

        async with local, remote, force_release(obj):
            oid = await asyncio.wait_for(local.add_service("test", obj), 5)

            proxied = await asyncio.wait_for(remote.get("test"), 5)
            async with timeout_context(proxied, 5):
                result = await asyncio.wait_for(proxied.invoke(test=id(self)), 5)
                self.assertEqual(result.data, {"x": id(self)%2000, "test": id(self)})

            async with timeout_context(await asyncio.wait_for(cli.get(proxied.name), 5), 5) as proxy2:
                with self.assertRaises(RPCCallFailed):
                    await asyncio.wait_for(proxy2.invoke(test=id(self)), 5)

            proxied = await asyncio.wait_for(remote.get("test"), 5)
            async with timeout_context(proxied, 5):
                result = await asyncio.wait_for(proxied.invoke(test=id(self)), 5)
                self.assertEqual(result.data, {"x": id(self)%2000, "test": id(self)})
        

    @with_registered_yuuno
    async def test_service_unregister(self):
        s1, s2 = pipe()
        local = ObjectManager(Server(s1))

        cli = Client(s2)
        remote = RemoteManager(cli)

        obj = DynTestObj({"x": id(self)%2000})

        async with local, remote, force_release(obj):
            oid = await asyncio.wait_for(local.add_service("test", obj), 5)

            self.assertTrue(await asyncio.wait_for(remote.has("test"), 5))

            proxied = await asyncio.wait_for(remote.get("test"), 5)
            async with timeout_context(proxied, 5):
                result = await asyncio.wait_for(proxied.invoke(test=id(self)), 5)
                self.assertEqual(result.data, {"x": id(self)%2000, "test": id(self)})

            await obj.release()

            self.assertFalse(await asyncio.wait_for(remote.has("test"), 5))
            with self.assertRaises(AttributeError):
                proxied = await asyncio.wait_for(remote.get("test"), 5)
                await proxied.acquire()