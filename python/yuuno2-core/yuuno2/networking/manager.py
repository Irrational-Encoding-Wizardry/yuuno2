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
from typing import Tuple

from yuuno2.resource_manager import Resource, register, on_release
from yuuno2.networking.rpc import Server, Client, RPCProxy
from yuuno2.networking.connection import BaseConnection
from yuuno2.networking.message import Message


class ObjectManager(Resource):
    MANAGER_ID = "a6eb965e-1c6a-4c23-897f-99ef0b9fb762"

    def __init__(self, server: Server):
        self.name = ObjectManager.MANAGER_ID
        self.server = server

        self.objects = {}
        self.uses = {}

    async def add_temporary_object(self, obj: Resource) -> str:
        await self.ensure_acquired()
        if obj.resource_state.released:
            raise ValueError("Object already released.")

        id = str(uuid.uuid4())
        self.objects[id] = obj
        on_release(obj, lambda _: self.objects.pop(id, None))
        return id

    async def add_service(self, name: str, obj: Resource):
        await self.ensure_acquired()

        await obj.acquire()
        register(self, obj)
        self.objects[name] = obj
        on_release(obj, lambda _: self.objects.pop(name, None))

    def on_version(self):
        self.ensure_acquired_sync()
        return Message({"version": 1, "extensions": []})

    def on_has_service(self, service: str):
        self.ensure_acquired_sync()
        return Message({
            "exists": service in self.objects
        })

    async def on_acquire_object(self, service: str):
        await self.ensure_acquired()
        if service not in self.objects:
            return Message({
                "exists": False
            })
        obj = self.objects[service]
        await obj.acquire()

        id = str(uuid.uuid4())
        registration = await self.server.register(id, obj)
        self.uses[id] = (registration, obj)
        on_release(registration, lambda _: self.uses.pop(id, None))

        return Message({
            "exists": True,
            "id": id
        })

    async def on_release_object(self, obj: str):
        await self.ensure_acquired()
        if obj not in self.uses:
            return Message({
                "removed": True
            })
        
        registration, obj = self.uses[obj]
        await registration.release()
        await obj.release(force=False)

        return Message({
            "removed": True
        })

    async def _acquire(self):
        await self.server.acquire()
        register(self.server, self)

        registration = await self.server.register(self.name, self)
        register(self, registration)
    
    async def _release(self):
        await self.server.release(force=False)


class ProxiedObject(RPCProxy):

    def __init__(self, manager: 'RemoteManager', client, name):
        super().__init__(client, name)
        self.manager = manager

    async def _acquire(self):
        await super()._acquire()
        self.name = await self.manager._acquire_object(self.name)

    async def _release(self):
        await self.manager._release_object(self.name)
        await super()._release()


class RemoteManager(Resource):

    def __init__(self, client: Client):
        self.client = client
        self.proxy = None

    async def has(self, name):
        await self.ensure_acquired()
        msg = await self.proxy.has_service(service=name)
        return msg.data.get("exists", False)

    async def get(self, name):
        await self.ensure_acquired()
        proxy = ProxiedObject(self, self.client, name)
        register(self, proxy)
        return proxy

    async def _acquire_object(self, name):
        await self.ensure_acquired()
        msg = await self.proxy.acquire_object(service=name)
        if not msg.data.get("exists", False):
            raise AttributeError("The proxied object does not exist.")
        return msg.data["id"]

    async def _release_object(self, name):
        await self.ensure_acquired()
        await self.proxy.release_object(obj=name)

    async def _acquire(self):
        await self.client.acquire()
        register(self.client, self)

        self.proxy = await self.client.get(ObjectManager.MANAGER_ID)
        await self.proxy.acquire()
        register(self, self.proxy)

    async def _release(self):
        await self.client.release(force=False)


def make_managed_connection(connection: BaseConnection) -> Tuple[ObjectManager, RemoteManager]:
    return ObjectManager(Server(connection)), RemoteManager(Client(connection))