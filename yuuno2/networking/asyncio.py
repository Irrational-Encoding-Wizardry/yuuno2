from asyncio import Protocol, BaseTransport, get_running_loop, Queue, ReadTransport, Event, Transport
from typing import NoReturn, Optional

from yuuno2.networking.base import Connection, Message
from yuuno2.networking.serializer import ByteOutputStream, ByteInputStream, bytes_protocol


class YuunoConnection(Connection):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        self.kwargs_proto = {
            name: kwargs.pop(name)
            for name in ["maxqueue"]
            if name in kwargs
        }

        self.protocol: Optional['ConnectionReaderProtocol'] = None
        self.transport: Optional[Transport] = None

        self.writing_active = Event()

    async def _acquire(self):
        loop = get_running_loop()
        self.transport, self.protocol = await loop.create_connection(
            lambda: ConnectionReaderProtocol(self, **self.kwargs_proto),
            *self.args, **self.kwargs
        )
        self.writing_active.set()

    async def _release(self):
        if not self.transport.is_closing():
            self.transport.close()
        self.writing_active.clear()

    async def read(self) -> Optional[Message]:
        await self.ensure_acquired()
        await self.protocol.read()

    async def write(self, message: Message):
        await self.ensure_acquired()
        await self.writing_active.wait()
        if not self.transport.is_closing():
            return
        self.transport.write(ByteOutputStream.write_message(message))


class ConnectionReaderProtocol(Protocol):

    def __init__(self, connection: YuunoConnection, maxqueue: int = 10):
        self.connection = connection
        self.transport: Optional[ReadTransport] = None

        self.protocol = bytes_protocol()
        self.queue = Queue()

        self.maxqueue = maxqueue

    def connection_made(self, transport: BaseTransport) -> None:
        if not isinstance(transport, ReadTransport):
            self.transport.close()
            raise IOError("Transport must be readable.")
        self.transport = transport

    def _release_connection(self):
        # Ignore queue-maxsize when closing as we are sure we cannot
        # receive any more data.
        if not self.protocol.closing:
            for message in self.protocol.close():
                self.queue.put_nowait(message)

        if not self.transport.is_closing():
            self.transport.close()

    def _advance_buffer(self, data: bytes = b""):
        if self.protocol.closed:
            return

        it = self.protocol.feed(data)
        while self.queue.qsize() < self.maxqueue:
            try:
                msg = next(it)
            except StopIteration:
                return
            except Exception:
                self.transport.close()
                raise

            self.queue.put_nowait(msg)

        if self.queue.qsize() >= self.maxqueue:
            self.transport.pause_reading()
        else:
            self.transport.resume_reading()

    async def read(self) -> Optional[Message]:
        value = await self.queue.get()
        self._advance_buffer()
        return value

    def connection_lost(self, exc: Optional[Exception]) -> None:
        self._release_connection()

    def eof_received(self) -> Optional[bool]:
        self._release_connection()

    def data_received(self, data: bytes) -> None:
        self._advance_buffer(data)

    def pause_writing(self) -> None:
        self.connection.writing_active.clear()

    def resume_writing(self) -> None:
        self.connection.writing_active.set()
