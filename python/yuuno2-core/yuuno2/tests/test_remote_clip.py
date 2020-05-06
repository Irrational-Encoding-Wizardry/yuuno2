
import asyncio
from functools import wraps

from aiounittest import AsyncTestCase

from yuuno2.resource_manager import Resource
from yuuno2.networking.message import Message
from yuuno2.networking.connection import pipe
from yuuno2.networking.rpc import Server, Client

from yuuno2.clips.remote import RemoteClip, ClipWrapper

from yuuno2.tests.utils import timeout_context, force_release, with_registered_yuuno
from yuuno2.tests.mocks import MockClip


class TestRemoteClip(AsyncTestCase):

    @with_registered_yuuno
    async def test_remote_clip(self):
        clip = MockClip()

        p1, p2 = pipe()
        srv = Server(p1)
        cli = Client(p2)

        async with clip, srv, cli:
            wrapper = ClipWrapper(clip)
            await wrapper.acquire()
            await srv.register("clip", wrapper)

            remote: RemoteClip = await asyncio.wait_for(RemoteClip.from_client(cli, "clip"), 5)
            async with timeout_context(remote, 5):
                meta = await asyncio.wait_for(remote.get_metadata(), 5)
                self.assertEqual(meta, {"id": id(clip)})

                async with timeout_context(remote[0], 5) as remote_frame, clip[0] as local_frame:
                    self.assertEqual(local_frame.size, remote_frame.size)
                    self.assertEqual(local_frame.native_format, remote_frame.native_format)
