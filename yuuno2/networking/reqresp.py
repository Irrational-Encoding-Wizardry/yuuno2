from typing import NamedTuple

from yuuno2.networking.base import Connection, MessageInputStream, Message, JSON
from yuuno2.resource_manager import register



class ReqRespServer(Connection):

    def __init__(self, parent: Connection):
        self.parent = parent
        super().__init__(parent.input, parent.output)

    async def _acquire(self):
        await self.acquire()
        register(self.parent, self)

    async def _release(self):
        pass

    async def handle_single_request(self):
        msg = await self.read()
        if msg is None:
            return False

        if "id" not in msg:
            await self.write(Message({'id': None, 'source': msg.values, 'type': 'error', 'error': 'ID missing from request-response.'}))
            return True
        id = msg['id']

        if "type" not in msg:
            await self.write(Message({'id': id, 'type': 'error', 'error': 'Type missing from frame.'}))
            return True
        type = msg['type']
        if type not in ('control', 'request'):
            await self.write(Message({'id': id, 'type': 'error', 'error': 'Invalid type. Excpected "control" or "request".'}))
            return True

    async def handle_control(self, message: JSON):
        if "type" not in message:


    async def run(self):
        async with self.parent:
            while True:
                if not (await self.handle_single_request()):
                    break

