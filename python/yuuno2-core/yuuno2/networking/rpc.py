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
import traceback
from typing import Any, Tuple
from asyncio import run_coroutine_threadsafe, CancelledError

from yuuno2.networking.connection import BaseConnection
from yuuno2.networking.message import Message

from yuuno2.asyncutils import coroutine, get_yuuno_loop

from yuuno2.resource_manager import register, on_release, Resource, SimpleResource


class Server(Resource):
    def __init__(self, connection: BaseConnection):
        self.connection = connection
        self.objects = {}

    async def register(self, name: str, obj: Any) -> SimpleResource:
        def _registration():
            self.objects[name] = obj
            yield
            del self.objects[name]

        reg = SimpleResource.from_generator(_registration(), obj=obj)
        await reg.acquire()
        register(self, reg)
        return reg

    async def _receive(self, message: Message):
        if message.data.get("type", None) != "invoke":
            return

        if "id" not in message.data:
            return

        id = message.data["id"]
        
        if "method" not in message.data:
            await self.connection.send(Message({"type": "error", "id": id, "message": "Method is missing"}))
            return
        if not message.data.get("target", ""):
            await self.connection.send(Message({"type": "error", "id": id, "message": "Target is missing"}))
            return

        target = message.data["target"]
        method = message.data["method"]
        payload = message.data.get("payload", {})
        if message.blobs:
            payload["_blobs"] = message.blobs

        get_yuuno_loop().create_task(self._invoke(id, target, method, payload))

    async def _invoke(self, id, target, method, payload):
        if target not in self.objects:
            await self.connection.send(Message({"type": "error", "id": id, "message": "Unknown target."}))
            return
            
        obj = self.objects[target]

        func = getattr(obj, f"on_{method}", getattr(obj, f"handle_unknown_method", None))
        if func is None:
            await self.connection.send(Message({"type": "error", "id": id, "message": "Unknown method."}))
            return
        
        try:
            result = await coroutine(func)(**payload)
        except Exception as e:
            formatted = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            await self.connection.send(Message({"type": "error", "id": id, "message": formatted}))
        else:
            await self.connection.send(Message({"type": "result", "id": id, "payload": result.data}, result.blobs))

    async def _acquire(self):
        await self.connection.acquire()
        register(self.connection, self)

        c = await self.connection.on_message(self._receive)
        register(self, c)

    async def _release(self):
        await self.connection.release(force=False)


class RPCCallFailed(Exception): pass


class RPCProxy(Resource):

    def __init__(self, client, name: str):
        self.client = client
        self.name = name

    def __getattr__(self, name):
        async def _proxy(**kwargs):
            blobs = kwargs.pop("_buffers", [])
            msg = Message(kwargs, blobs)
            fut = await self.client._call(self.name, name, msg)

            res = SimpleResource(fut)
            await res.acquire()
            register(self, res)
            fut.add_done_callback(lambda _: get_yuuno_loop().create_task(res.release()))
            on_release(res, lambda _: fut.cancel())

            return await fut

        return _proxy

    async def _acquire(self):
        pass

    async def _release(self):
        pass


class Client(Resource):

    def __init__(self, connection: BaseConnection):
        self.connection = connection
        self.requests = {}
        self._current_id = 0

    @property
    def __next_id(self):
        val = self._current_id
        self._current_id += 1
        return val

    async def _receive(self, message):
        if message.data.get("type", None) not in {"error", "result"}:
            return

        if "id" not in message.data:
            return

        id = message.data["id"]

        if id not in self.requests:
            return
        
        request = self.requests[id]
        if message.data["type"] == "error":
            exc = RPCCallFailed(message.data.get("message"))
            request.set_exception(exc)
        else:
            request.set_result(Message(message.data.get("payload", {}), message.blobs))

    async def get(self, name):
        proxy = RPCProxy(self, name)
        await proxy.acquire()
        register(self, proxy)
        return proxy

    async def _call(self, target, method, message, **addendum):
        id = self.__next_id

        fut = get_yuuno_loop().create_future()
        self.requests[id] = fut
        fut.add_done_callback(lambda _: self.requests.pop(id, None))

        msg = Message({
            "id": id,
            "type": "invoke",
            "target": target,
            "method": method,
            "payload": message.data
        }, message.blobs)
        await self.connection.send(msg)
        return fut

    async def _acquire(self):
        await self.connection.acquire()
        register(self.connection, self)

        c = await self.connection.on_message(self._receive)
        register(self, c)

    async def _release(self):
        for request in tuple(self.requests.values()):
            request.cancel()
        self.requests = {}
        await self.connection.release(force=False)


def make_client_server_on(connection: BaseConnection) -> Tuple[Server, Client]:
    srv = Server(connection)
    cli = Client(connection)
    return srv, cli
