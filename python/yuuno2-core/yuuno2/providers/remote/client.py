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
from typing import Mapping, Union, Any, Sequence, Iterator, Optional

from yuuno2.clip import Clip
from yuuno2.clips.remote import RemoteClip
from yuuno2.networking.base import Connection
from yuuno2.networking.reqresp import ReqRespClient, function
from yuuno2.providers.remote.helpers import MultiplexedClient, TYPE_MAP_RECV, TYPE_MAP_SEND
from yuuno2.script import Script, NOT_GIVEN, ScriptProvider
from yuuno2.typings import ConfigTypes


class LazyClip(RemoteClip):

    def __init__(self, remote: 'RemoteScript', clip: str):
        super().__init__(None)
        self._remote = remote
        self._clip = clip
        self._channel_name = f"clip:{id(self)}"

    async def _acquire(self) -> None:

        await self._remote._client.register_clip(channel=self._channel_name, name=self._clip)
        self.connection = self._remote._multiplexer.connect(self._channel_name)
        await super()._acquire()

    async def _release(self) -> None:
        await self._remote._client.unregister_clip(channel=self._channel_name)
        await super()._release()


class LazyClipMapping(Mapping[str, Clip]):

    def __init__(self, clips: Sequence[str], remote: 'RemoteScript'):
        self.clips = clips
        self.remote = remote

    def __getitem__(self, k: str) -> Clip:
        if k not in self.clips:
            raise KeyError(k)

        return LazyClip(self.remote, k)

    def __len__(self) -> int:
        return len(self.clips)

    def __iter__(self) -> Iterator[str]:
        return iter(self.clips)


class RemoteScriptClient(ReqRespClient):
    set_config = function()
    get_config = function()
    list_config = function()

    run = function()
    list_clips = function()
    register_clip = function()
    unregister_clip = function()


class RemoteScript(Script, MultiplexedClient):

    def create_client(self, connection: Connection) -> ReqRespClient:
        return RemoteScriptClient(connection)

    def activate(self) -> None:
        # Ignored.
        pass

    def deactivate(self) -> None:
        # Ignored
        pass

    async def set_config(self, key: str, value: ConfigTypes) -> None:
        cls = type(value)
        typename, send = TYPE_MAP_SEND[cls]
        converted, bufs = send(value)
        await self._client.set_config(key=key, value=converted, type=typename, _buffers=bufs)

    async def get_config(self, key: str, default: Union[object, ConfigTypes] = NOT_GIVEN) -> ConfigTypes:
        result, buffers = await self._client.get_config(key=key)
        if result["type"] == "unset":
            if default is NOT_GIVEN:
                raise KeyError(key)

            return default
        conv = TYPE_MAP_RECV[result["type"]]
        return conv(result["value"], buffers)

    async def list_config(self) -> Sequence[str]:
        return (await self._client.list_config())[0]["keys"]

    async def run(self, code: Union[bytes, str]) -> Any:
        encoding = None
        if isinstance(code, str):
            code = code.encode("utf-8")
            encoding = "utf-8"

        await self._client.run(encoding=encoding, _buffers=[code])

    async def retrieve_clips(self) -> Mapping[str, Clip]:
        msg, _ = await self._client.list_clips()
        return LazyClipMapping(msg["clips"], self)


class LazyRemoteScript(RemoteScript):

    def __init__(self, remote: 'RemoteScriptProvider', params: Mapping[str, Any]):
        super().__init__(None)
        self._remote = remote
        self._params = params
        self._script_name = f"script:{id(self)}"

    async def _acquire(self) -> None:
        await self._remote._client.create_script(channel_name=self._script_name, params=self._params)
        self.connection = self._remote._multiplexer.connect(self._script_name)
        return (await super()._acquire())

    async def _release(self) -> None:
        await self._remote._client.release_script(channel_name=self._script_name)
        return (await super()._release())


class ScriptProviderClient(ReqRespClient):
    create_script = function()
    release_script = function()


class RemoteScriptProvider(ScriptProvider, MultiplexedClient):
    async def get(self, **params: Mapping[str, Any]) -> Optional[Script]:
        return LazyRemoteScript(self, params)

    def create_client(self, connection: Connection) -> ReqRespClient:
        return ScriptProviderClient(connection)