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
import inspect
from asyncio import Future, get_running_loop
from traceback import format_exception
from typing import List, Mapping, Awaitable, Callable, Optional, MutableMapping, Union, cast

from yuuno2.networking.base import Connection, Message, JSON
from yuuno2.networking.reader import ReaderTask
from yuuno2.resource_manager import register


class ReqRespServerException(Exception): pass
class CallFailed(RuntimeError): pass


class function(object):

    def __init__(self):
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner) -> Callable[..., Awaitable[Message]]:
        def _wrapper(**kwargs):
            buffers = kwargs.pop("_buffers", [])
            return instance._call(self.name, buffers, kwargs)
        _wrapper.__name__ = self.name
        return _wrapper


class ReqRespClient(Connection):

    def __init__(self, parent: Connection):
        self.parent = parent
        self._waiters: MutableMapping[int, Future[Message]] = {}
        self._current_id = 0
        super().__init__(parent.input, parent.output)

    async def _call(self, funcname: str, buffers: List[bytes], params: Mapping[str, JSON]) -> Awaitable[Message]:
        cid = self._current_id
        self._current_id += 1

        future = get_running_loop().create_future()
        self._waiters[cid] = future

        await self.write(Message({"method": funcname, "type": "request", "id": cid, "params": params}, buffers))

        return (await future)

    async def _delivered(self, raw: Optional[Message]):
        if raw is None:
            waiters = self._waiters
            self._waiters = None
            for v in waiters.values():
                v.cancel()
            return

        msg, buffers = raw
        if "id" not in msg:
            return

        id = msg["id"]
        future: Future[Message] = self._waiters.pop(id, None)
        if future is None:
            return

        if "type" not in msg:
            future.set_exception(ReqRespServerException("Missing type in server response."))
            return

        type = msg["type"]
        if type == "error":
            future.set_exception(CallFailed(msg.get("error", "The requested funtion failed.")))
        else:
            future.set_result(Message(msg["result"], buffers))

    async def _acquire(self):
        await self.parent.acquire()
        register(self.parent, self)

        reader = ReaderTask(self.parent.input, self._delivered)
        register(self, reader)
        await reader.acquire()

    async def _release(self):
        await self.parent.release(force=False)


class ReqRespServer(Connection):

    def __init__(self, parent: Connection):
        self.parent = parent
        super().__init__(parent.input, parent.output)

    async def _acquire(self):
        await self.parent.acquire()
        register(self.parent, self)

        task = ReaderTask(self.parent.input, self.handle_single_request)
        await task.acquire()
        register(self, task)

    async def _release(self):
        await self.parent.release(force=False)

    async def handle_request(self, id, msg: JSON, buffers: List[bytes]):
        try:
            if "method" not in msg:
                raise ReqRespServerException("No method given.")
            method = msg['method']

            func = getattr(self, "on_" + method.lower(), None)
            if func is None:
                raise ReqRespServerException("Unknown method.")

            additional = {}
            if len(buffers) > 0:
                additional["_buffers"] = buffers
            result: Union[Awaitable[Message], Message] = func(**additional, **msg.get('params', {}))
            if inspect.isawaitable(result):
                result = await result
            result: Message = cast('Message', result)

            return Message({"id": id, "type": "response", "result": result.values}, result.blobs)

        except ReqRespServerException:
            raise

        except Exception as e:
            exc = ''.join(format_exception(type(e), e, e.__traceback__))
            raise ReqRespServerException("An error occured while executing the function:\n" + exc) from None

    async def handle_single_request(self, raw: Optional[Message]):
        if raw is None:
            return

        msg, buffers = raw

        if "id" not in msg:
            await self.write(Message({
                'id': None,
                'type': 'error',
                'error': 'ID missing from request-response.'
            }))
            return

        id = msg['id']

        try:
            if "type" not in msg:
                raise ReqRespServerException("Type missing from request.")
            type = msg["type"]

            if type == "request":
                result: Message = await self.handle_request(id, msg, buffers)
                await self.write(result)

            else:
                raise ReqRespServerException('Type missing from frame.')

        except ReqRespServerException as e:
            await self.write(Message({'id': id, 'type': 'error', 'error': str(e)}))
