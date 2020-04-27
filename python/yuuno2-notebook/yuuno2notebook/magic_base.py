import functools
from asyncio import run_coroutine_threadsafe, coroutine

from IPython import get_ipython
from IPython.core.magic import Magics, line_cell_magic, line_magic, cell_magic, magic_kinds

from yuuno2.resource_manager import NonAbcResource
from yuuno2notebook.utils import delay_call, run_in_main_thread

__all__ = ["ResourceMagics", "line_magic", "cell_magic", "line_cell_magic"]


def as_async_command(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        return delay_call(coroutine(func)(*args, **kwargs))
    return _wrapper


class ResourceMagics(Magics, NonAbcResource):

    def _delayed_acquire(self):
        ipython = get_ipython()
        ipython.magics_manager.register(self)

    def _delayed_release(self):
        ipython = get_ipython()
        mgr = ipython.magics_manager

        for kind in magic_kinds:
            for key in self.magics[kind]:
                del mgr.magics[kind][key]

    async def _acquire(self):
        await run_in_main_thread(self._delayed_acquire)

    async def _release(self):
        await run_in_main_thread(self._delayed_release)