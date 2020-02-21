import asyncio
from asyncio import get_running_loop
from typing import NoReturn

from IPython import InteractiveShell
from tornado.ioloop import IOLoop


def get_running_aio_loop() -> asyncio.AbstractEventLoop:
    tornado_loop = IOLoop.current()
    loop = getattr(tornado_loop, "asyncio_loop", None)
    if loop is None:
        loop = get_running_loop()
    return loop


async def _wrap_delayed_call(ipy: InteractiveShell, coro):
    ipy.push({'$$y_init_coro': None}, interactive=False)

    try:
        await coro
    except Exception as e:
        import sys
        import traceback
        print("Error during Yuuno2-Notebook State Change:", file=sys.stderr)
        traceback.print_exception(type(e), e, e.__traceback__)


def delay_call(ipy: InteractiveShell, coro) -> NoReturn:
    """
    This is a hack:

    by injecting a run_cell command with an await, we get IPython to run the async code
    exclusively.

    :param ipy:   The Ipython instance.
    :param coro:  The coroutine to run.
    :return:
    """
    _wrapped = _wrap_delayed_call(ipy, coro)

    ipy.push({"$$y_init_coro": coro}, interactive=False)
    loop = get_running_aio_loop()

    asyncio.run_coroutine_threadsafe(
        ipy.run_cell_async(
            "await locals()['$$y_init_coro'][0]",
            silent=True, shell_futures=False
        ),
        loop=loop
    )
