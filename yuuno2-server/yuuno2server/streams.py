import asyncio
import concurrent
import sys
from threading import Thread, Event, Lock
from asyncio import get_running_loop, sleep, AbstractEventLoop, Event as AEvent
from concurrent.futures import ThreadPoolExecutor
from typing import NoReturn, Optional

from yuuno2.asyncutils import dynamic_timeout
from yuuno2.networking.base import Message

if sys.platform.startswith("win"):
    import ctypes
    from ctypes import wintypes
    kernel32 = ctypes.WinDLL("kernel32")

else:
    import select

from yuuno2.networking.serializer import ByteInputStream, ByteOutputStream

io_pool = ThreadPoolExecutor(max_workers=10)


class FileOutputStream(ByteOutputStream):

    def __init__(self, fobj):
        self.fobj = fobj
        self.io_lock = Lock()
        super().__init__()

    def _send(self, data: bytes) -> None:
        with self.io_lock:
            if self.fobj.closed:
                return

            self.fobj.write(data)
            self.fobj.flush()

    def _close(self):
        with self.io_lock:
            self.fobj.close()

    async def send(self, data: bytes) -> None:
        await get_running_loop().run_in_executor(io_pool, self._send, data)

    async def close(self) -> NoReturn:
        await get_running_loop().run_in_executor(io_pool, self._close)

    async def _acquire(self) -> NoReturn:
        pass

    async def _release(self) -> NoReturn:
        await self.close()


class FileInputStream(ByteInputStream):

    def __init__(self, fobj):
        self.fobj = fobj
        self.reader = Thread(target=self._readloop, args=(get_running_loop(),))
        self._closed = AEvent()
        self._queue_open = Event()
        self._queue_open.set()

        self._cancel_current_io_op = None

        super().__init__()

    def queue_active(self):
        self._queue_open.set()

    def queue_filled(self):
        self._queue_open.clear()

    async def read(self) -> Optional[Message]:
        if self._closed.is_set() or self.fobj.closed:
            return

        try:
            return await dynamic_timeout(super().read(), self._closed.wait())
        except asyncio.TimeoutError:
            if self._closed.is_set():
                return None
            raise

    if sys.platform.startswith("win"):
        def _read_cancellable(self):
            if self.fobj.closed:
                return

            current_process = kernel32.GetCurrentProcess()
            current_thread = kernel32.GetCurrentThread()

            target = wintypes.HANDLE(-1)

            kernel32.DuplicateHandle(current_process, current_thread, current_process, ctypes.byref(target), 0, 0, 2)

            _cancel_token = [target.value, False]
            self._cancel_current_io_op = _cancel_token

            try:
                return self.fobj.read(1)
            except Exception as e:
                if not (_cancel_token[1] or self._closed.is_set()):
                    raise e
            finally:
                self._cancel_current_io_op = None
                kernel32.CloseHandle(_cancel_token[0])

        def _cancel_read(self):
            if self._cancel_current_io_op is None:
                return

            token = self._cancel_current_io_op
            token[1] = True
            kernel32.CancelSynchronousIo(token[0])

    else:
        def _read_cancellable(self):
            _cancel_atom = [Event()]
            self._cancel_current_io_op = _cancel_atom
            while not _cancel_atom[0].is_set():
                r, _, _ = select.select([self.fobj], [], [], timeout=0)
                if not r:
                    _cancel_atom[0].wait(.1)
                    continue

                self._cancel_current_io_op = None
                return self.fobj.read(1)

        def _cancel_read(self):
            if self._cancel_current_io_op is None:
                return

            self._cancel_current_io_op[0].set()

    def _readloop(self, loop: AbstractEventLoop):
        while not (self.fobj.closed or self._closed.is_set()):
            # Backpressure protocol.
            self._queue_open.wait(1)
            if not self._queue_open.is_set():
                continue

            b = self._read_cancellable()
            loop.call_soon_threadsafe(self.feed, b)
            if not b:
                break

        if not self._closed.is_set():
            loop.call_soon_threadsafe(self._closed.set)

    def is_closed(self):
        return self._closed.is_set()

    async def _acquire(self) -> NoReturn:
        self.reader.start()
        await super()._acquire()

    async def _release(self) -> NoReturn:
        self._queue_open.clear()

        if not self._closed.is_set():
            self._closed.set()
            self._cancel_read()
            self.fobj.close()

        while self.reader.is_alive():
            await sleep(0.1)

        await super()._release()
