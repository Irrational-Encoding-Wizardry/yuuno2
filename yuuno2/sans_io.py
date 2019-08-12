import functools
from collections import deque
from typing import NoReturn, Coroutine, TypeVar, Generic, Optional, Iterator, Any, Callable


class Buffer(object):

    def __init__(self):
        self._size = 0
        self._cursor = 0
        self._buffer = deque()

    def _get_fragment(self) -> bytes:
        if not self._buffer:
            return b''

        part = self._buffer.popleft()
        if self._cursor > 0:
            return part[:self._cursor]
        else:
            return part

    def _read(self, length: int = 0) -> bytes:
        if len(self._buffer) == 0:
            return b''

        if length == 0:
            first = self._get_fragment()

            self._cursor = 0
            self._size = 0

            if len(self._buffer) == 1:
                return first

            data = b''.join([first] + self._buffer)
            self._buffer.clear()
            return data

        parts = []
        while length > 0 and len(self._buffer) > 0:
            part = self._buffer.popleft()

            if len(part) > self._cursor+length:
                part = part[self._cursor:self._cursor+length]
                self._cursor += length
                parts.append(part)
                self._buffer.appendleft(part)
                break

            if self._cursor > 0:
                part = part[self._cursor:]

            parts.append(part)
            length -= len(part)
            self._cursor = 0

        result = b''.join(parts)
        self._size -= len(result)
        return result

    def peek(self, length: int = 0) -> bytes:
        data = self._read(length)

        fragment = self._get_fragment()
        if fragment:
            self._buffer.appendleft(fragment)

        if data:
            self._buffer.appendleft(data)
            self._size += data

        return data

    def read(self, length: int = 0) -> bytes:
        return self._read(length)

    def feed(self, data: bytes) -> NoReturn:
        self._buffer.append(data)
        self._size += len(data)

    def __len__(self):
        return self._size


T = TypeVar("T")
A = TypeVar("A")


class _Action(Generic[A]):

    def __await__(self) -> A:
        return (yield self)


_Close = type("_Close", (_Action[None],), {})()


class peek(_Action[bytes]):
    """
    Reads up between zero and length bytes but does not consume it.
    If length is zero it return the entire buffer.
    """

    def __init__(self, length: int = 0):
        self.length = length


class read(_Action[bytes]):
    """
    Reads up between zero and length bytes. If length is zero it
    consumes the entire buffer.
    """

    def __init__(self, length: int = 0):
        self.length = length


class left(_Action[Optional[int]]):
    pass


class wait(_Action[None]):
    """
    Waits until at least `length` bytes are read.
    """
    def __init__(self, length: int = 1):
        if length <= 0:
            raise ValueError("length must be > 1")
        self.length = length


async def read_exactly(length: int = 1) -> bytes:
    await wait(length)
    data = await read(length)
    if len(data) < length:
        raise ConnectionResetError
    return data


class emit(_Action[None], Generic[T]):
    """
    Returns a new value to the feed function.
    """

    def __init__(self, data: T):
        self.data = data


class Consumer(Generic[T]):

    def __init__(self, coro: Coroutine[_Action, Any, None]):
        self.coro = coro
        self.buffer = Buffer()
        self.queue = deque()

        self._feed_coro(None)

    def _feed_coro(self, data: Any) -> NoReturn:
        # Prime the coroutine.
        try:
            action = self.coro.send(data)
        except StopIteration:
            action = _Close

        self.queue.append(action)

    def _handle_feed(self) -> Optional[T]:
        for op in iter(self.queue.popleft(), _Close):
            if isinstance(op, emit):
                return op.data
            elif isinstance(op, wait):
                if len(self.buffer) == op.length:
                    self.queue.appendleft(op)
                    return
                self._feed_coro(None)
            elif isinstance(op, peek):
                self._feed_coro(self.buffer.peek(op.length))
            elif isinstance(op, read):
                self._feed_coro(self.buffer.read(op.length))
            elif isinstance(op, left):
                self._feed_coro(len(self.buffer))

    def _handle_closed(self) -> Optional[T]:
        for op in iter(self.queue.popleft(), _Close):
            if isinstance(op, emit):
                self._feed_coro(None)
                return op.data
            elif isinstance(op, wait):
                self._feed_coro(b'')
            elif isinstance(op, peek):
                self._feed_coro(self.buffer.peek(op.length))
            elif isinstance(op, read):
                self._feed_coro(self.buffer.read(op.length))
            elif isinstance(op, left):
                bufsize = len(self.buffer)
                if bufsize == 0:
                    bufsize = None
                self._feed_coro(bufsize)

    def feed(self, data: Optional[bytes]) -> Iterator[T]:
        if self.queue[0] is _Close:
            raise ConnectionResetError("Connection closed.")

        self.buffer.feed(data)
        yield from iter(self._handle_feed, None)


def protocol(func: Callable[[...], Coroutine[_Action, Any, None]]) -> Callable[[...], Consumer[Any]]:
    @functools.wraps(func)
    def _wrapped(*args, **kwargs) -> Consumer:
        coro = func(*args, **kwargs)
        return Consumer(coro)
    return _wrapped