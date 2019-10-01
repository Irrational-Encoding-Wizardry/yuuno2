import asyncio
from asyncio import get_running_loop

from tornado.ioloop import IOLoop


def get_running_aio_loop() -> asyncio.AbstractEventLoop:
    tornado_loop = IOLoop.current()
    loop = getattr(tornado_loop, "asyncio_loop", None)
    if loop is None:
        loop = get_running_loop()
    return loop
