##
# Stub for %load_ext yuuno
from asyncio import get_running_loop

from tornado.ioloop import IOLoop
from IPython import InteractiveShell
from ipykernel.zmqshell import ZMQInteractiveShell

from yuuno2notebook.environment import Yuuno2Notebook

import asyncio

from yuuno2notebook.utils import get_running_aio_loop


async def _delay_call(coro):
    try:
        await coro
    except Exception as e:
        import sys
        import traceback
        print("Error during Yuuno2-Notebook State Change:", file=sys.stderr)
        traceback.print_exception(type(e), e, e.__traceback__)
    else:
        print("Plugin activacted.")


def load_ipython_extension(ipython: InteractiveShell) -> None:
    """
    Called when IPython load this extension.
    :param ipython:  The current IPython-console instance.
    """
    if not isinstance(ipython, ZMQInteractiveShell):
        raise EnvironmentError("Yuuno2 can only run from an IPython-Notebook.")

    environment = Yuuno2Notebook.instance(shell=ipython)
    if environment.shell != ipython or environment.acquired:
        raise EnvironmentError("Yuuno2 is already active.")

    loop = get_running_aio_loop()
    asyncio.run_coroutine_threadsafe(_delay_call(environment.acquire()), loop=loop)


def unload_ipython_extension(ipython: InteractiveShell) -> None:
    """
    Called when IPython unloads the extension.
    """
    instance = Yuuno2Notebook.instance()
    if not instance.acquired:
        return

    asyncio.run_coroutine_threadsafe(_delay_call(instance.release(force=True)), loop=ipython.active_eventloop)
