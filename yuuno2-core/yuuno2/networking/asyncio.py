from asyncio import Protocol, BaseTransport, get_running_loop, sleep
from asyncio import Queue, Event, Transport, ensure_future, TimeoutError
from typing import Optional, NoReturn
from weakref import WeakKeyDictionary

from yuuno2.asyncutils import dynamic_timeout
from yuuno2.networking.base import Message, MessageInputStream, MessageOutputStream
from yuuno2.networking.serializer import ByteOutputStream, bytes_protocol
from yuuno2.resource_manager import ResourceProxy, remove_callback, on_release


class ResourceDescriptor(object):

    def __init__(self):
        self._refs = WeakKeyDictionary()

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self._refs.get(instance, None)

    def _unset_by_expiry(self, rs):
        if isinstance(rs, ResourceProxy):
            rs = rs.target

        if rs in self._refs:
            del self._refs[rs]

    def __set__(self, instance, value):
        if instance in self._refs:
            prev = self._refs.pop(instance)
            if value is not None:
                remove_callback(prev, self._unset_by_expiry)

        self._refs[instance] = value
        if value is not None:
            on_release(value, self._unset_by_expiry)

    def __delete__(self, instance):
        if instance in self._refs:
            old = self._refs.pop(instance)
            if old is not None:
                remove_callback(old, self._unset_by_expiry)


class YuunoProtocol(Protocol):
    QUEUE_MAXSIZE = 30

    _ingress: Optional[MessageInputStream] = ResourceDescriptor()
    _egress: Optional[MessageOutputStream] = ResourceDescriptor()

    def __init__(self):
        self.transport: Optional[Transport] = None
        self.protocol = bytes_protocol()
        self.rqueue = Queue()

        self._transport_gate = Event()
        self._closed = Event()

    async def _close(self):
        if self._ingress is not None:
            await self._ingress.release(force=True)
        if self._egress is not None:
            await self._egress.release(force=True)

    async def read_next_message(self) -> Optional[Message]:
        if self._closed.is_set():
            return

        try:
            return await dynamic_timeout(self.rqueue.get(), self._closed.wait())
        except TimeoutError:
            return None

    async def write_message(self, message: Message):
        if self._closed.is_set():
            return

        try:
            await dynamic_timeout(self._transport_gate.wait(), self._closed.wait())
        except TimeoutError:
            return

        self.transport.write(ByteOutputStream.write_message(message))

    async def close(self):
        self.transport.close()

    def connection_made(self, transport: BaseTransport) -> None:
        self.transport = transport
        self._transport_gate.set()

    def _parse_until(self, maxsize: Optional[int] = QUEUE_MAXSIZE):
        if maxsize is not None and self.rqueue.qsize()>=maxsize:
            return False

        for msg in self.protocol.feed(b""):
            self.rqueue.put_nowait(msg)
            if maxsize is not None and self.rqueue.qsize() >= maxsize:
                return False

        return True

    def data_received(self, data: bytes) -> None:
        self.protocol.feed(data)
        if not self._parse_until(maxsize=self.QUEUE_MAXSIZE):
            self.transport.resume_reading()

    def pause_writing(self) -> None:
        self._transport_gate.clear()

    def resume_writing(self) -> None:
        self._transport_gate.set()

    def connection_lost(self, exc: Optional[Exception]) -> None:
        self._transport_gate.clear()
        self._closed.set()
        ensure_future(self._close(), loop=get_running_loop())
        self._parse_until(None)


class ConnectionInputStream(MessageInputStream):

    def __init__(self, protocol: YuunoProtocol):
        self.protocol = protocol

    async def read(self) -> Optional[Message]:
        return await self.protocol.read_next_message()

    async def _acquire(self) -> NoReturn:
        self.protocol._ingress = self

    async def _release(self) -> NoReturn:
        self.protocol._ingress = None


class ConnectionOutputStream(MessageOutputStream):

    def __init__(self, protocol: YuunoProtocol):
        self.protocol = protocol

    async def write(self, message: Message) -> NoReturn:
        await self.protocol.write_message(message)
        await sleep(0)

    async def close(self) -> NoReturn:
        await self.protocol.close()

    async def _acquire(self) -> NoReturn:
        self.protocol._egress = self

    async def _release(self) -> NoReturn:
        if self.protocol._egress is self:
            await self.close()

        self.protocol._egress = None