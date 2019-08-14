import json
import array
import itertools
import sys
from abc import abstractmethod, ABC
from asyncio import Queue
from typing import NoReturn, Optional

from yuuno2.networking.base import Message, MessageOutputStream, MessageInputStream
from yuuno2.sans_io import protocol, read_exactly, emit, Consumer


@protocol
async def bytes_protocol():
    try:
        while True:
            sz: bytes = await read_exactly(4)
            length = int.from_bytes(sz, 'big')

            hdr = await read_exactly(length*4)
            data = array.array.frombytes('L', hdr)
            if sys.byteorder != "big":
                data.byteswap()

            text, *buffers = [(await read_exactly(l)) for l in data]

            text = text.encode("utf-8")
            text = json.loads(text)

            await emit(Message(text, buffers))
    except ConnectionResetError:
        pass

class ByteOutputStream(MessageOutputStream, ABC):


    def write_message(self, message: Message) -> bytes:
        parts = [None]

        text, buffers = message
        parts.append(json.dumps(text, ensure_ascii=True).encode("utf-8"))
        parts.extend(buffers)

        hdr = array.array(
            'L',
            [len(parts)] + [len(part) for part in itertools.islice(parts, 1, None, None)]
        )
        if sys.byteorder != "big":
            hdr.byteswap()
        parts[0] = hdr.to_bytes()

        return b''.join(parts[0])

    @abstractmethod
    async def send(self, data: bytes) -> None:
        pass

    async def write(self, message: Message) -> NoReturn:
        pass


class ByteInputStream(MessageInputStream):

    def __init__(self):
        self.protocol: Consumer[Message] = bytes_protocol()
        self.queue = Queue()

    async def feed(self, data: bytes):
        for message in self.protocol.feed(data):
            await self.queue.put(message)

    async def read(self) -> Optional[Message]:
        return (await self.queue.get())
