import functools
from types import new_class
from collections import deque
from typing import NoReturn, Coroutine, TypeVar, Generic, Optional, Iterator, Any, Callable, Type


class Buffer(object):

    def __init__(self):
        self._size = 0
        self._cursor = 0
        self._buffer = deque()

        self._closed = False

    def _get_fragment(self) -> bytes:
        if not self._buffer:
            return b''

        part = self._buffer.popleft()
        if self._cursor > 0:
            return part[self._cursor:]
        else:
            return part

    def _read(self, length: int = 0) -> bytes:
        if len(self._buffer) == 0:
            return b''

        if length == 0:
            first = self._get_fragment()

            self._cursor = 0
            self._size = 0

            if len(self._buffer) == 0:
                return first

            data = b''.join([first] + list(self._buffer))
            self._buffer.clear()
            return data

        parts = []
        while length > 0 and len(self._buffer) > 0:
            part = self._buffer.popleft()

            if len(part) > self._cursor+length:
                self._buffer.appendleft(part)
                part = part[self._cursor:self._cursor+length]
                parts.append(part)
                self._cursor += length
                break

            if self._cursor > 0:
                part = part[self._cursor:]

            parts.append(part)
            length -= len(part)
            self._cursor = 0

        result = b''.join(parts)
        self._size -= len(result)
        return result

    def peek(self, length: int = 0) -> Optional[bytes]:
        if len(self._buffer) == 0 and self._closed:
            return None

        data = self._read(length)

        fragment = self._get_fragment()
        if fragment:
            self._buffer.appendleft(fragment)

        if data:
            self._buffer.appendleft(data)
            self._size += len(data)

        return data

    def read(self, length: int = 0) -> Optional[bytes]:
        if len(self._buffer) == 0 and self._closed:
            return None

        return self._read(length)

    def feed(self, data: Optional[bytes]) -> NoReturn:
        if self._closed:
            raise IOError("Feeding closed buffer.")

        if data is None:
            self.close()
            return

        if len(data) == 0:
            return

        self._buffer.append(data)
        self._size += len(data)

    def close(self) -> NoReturn:
        self._closed = True

    @property
    def closing(self) -> bool:
        return self._closed

    @property
    def closed(self) -> bool:
        return len(self) == 0 and self.closing

    def __len__(self):
        return self._size


T = TypeVar("T")
A = TypeVar("A")


class PauseProtocol(BaseException):
    def __init__(self, value: Any):
        self.value = value


class EmitEvent(BaseException):
    def __init__(self, value: Any):
        self.value = value


class _Action(Generic[A]):

    def __await__(self) -> A:
        return (yield self)

    def handle(self, consumer: 'Consumer') -> Optional[A]:
        pass

    @classmethod
    def operation(cls: '_Action[A]', func: Callable[..., Optional[A]]) -> Type['_Action[A]']:
        def _init(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def _handle(self, consumer):
            func(consumer, *self.args, *self.kwargs)

        return new_class(
            func.__name__,
            (cls, ),
            {},
            lambda ns: ns.update({'__init__':_init, 'handle': _handle})
        )


class Consumer(Generic[T]):

    _return = _Action.operation(lambda _, v: v)

    def __init__(self, coro: Coroutine[_Action, Any, None]):
        self.coro = coro
        self.buffer = Buffer()
        self.queue = deque()
        self._closed = False

        self._feed_coro(None)

    @property
    def closed(self) -> bool:
        return self._closed

    def close(self):
        self._closed = True

    def _next(self) -> Optional[_Action]:
        if len(self.queue) == 0:
            return

        return self.queue.popleft()

    def _feed_coro(self, data: Any) -> NoReturn:
        # Prime the coroutine.
        try:
            action = self.coro.send(data)
        except StopIteration:
            action = close()
            self._closed = True

        self.queue.append(action)

    def _handle_feed(self) -> Optional[T]:
        for op in iter(self._next, None):
            try:
                value = op.handle(self)
            except PauseProtocol as e:
                self.queue.appendleft(self._return(e.value))
                break
            except EmitEvent as e:
                return e.value

            self._feed_coro(value)

    def feed(self, data: Optional[bytes]) -> Iterator[T]:
        self.buffer.feed(data)
        yield from iter(self._handle_feed, None)


def protocol(func: Callable[..., Coroutine[_Action, Any, None]]) -> Callable[..., Consumer[Any]]:
    @functools.wraps(func)
    def _wrapped(*args, **kwargs) -> Consumer:
        coro = func(*args, **kwargs)
        return Consumer(coro)
    return _wrapped


@_Action.operation
def close(consumer: Consumer) -> None:
    consumer.close()


@_Action.operation
def peek(consumer: Consumer, length: int = 0) -> bytes:
    return consumer.buffer.peek(length)


@_Action.operation
def read(consumer: Consumer, length: int = 0) -> bytes:
    return consumer.buffer.read(length)


@_Action.operation
def left(consumer: Consumer) -> int:
    return len(consumer.buffer)


@_Action.operation
def closing(consumer: Consumer) -> bool:
    return consumer.buffer.closing


@_Action.operation
def sleep(consumer: Consumer) -> bool:
    if consumer.buffer.closing:
        return False
    raise PauseProtocol(True)


@_Action.operation
def emit(_: Consumer, value: Any) -> None:
    raise EmitEvent(value)


async def wait(length: int = 1) -> None:
    while length < (await left()):
        if not (await sleep()):
            # Buffer is closing. Prevent sleeping.
            return


async def read_exactly(length: int = 1) -> bytes:
    await wait(length)
    data = await read(length)
    if len(data) < length:
        raise ConnectionResetError
    return data
