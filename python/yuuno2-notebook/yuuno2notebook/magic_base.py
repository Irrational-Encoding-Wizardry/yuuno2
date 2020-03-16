import functools
from asyncio import run_coroutine_threadsafe

from IPython import get_ipython
from IPython.core.magic import Magics, line_cell_magic, line_magic, cell_magic, magic_kinds

from yuuno2.resource_manager import NonAbcResource
from yuuno2notebook.utils import get_running_aio_loop

__all__ = ["ResourceMagics", "line_magic", "cell_magic", "line_cell_magic"]


def as_async_command(func):
    async def _fire_but_show_exc(coro):
        try:
            await coro
        except Exception as e:
            import traceback
            traceback.print_exception(type(e), e, e.__traceback__)

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        loop = get_running_aio_loop()
        run_coroutine_threadsafe(_fire_but_show_exc(func(*args, **kwargs)), loop)
        return None
    return _wrapper


class ResourceMagics(Magics, NonAbcResource):

    async def _acquire(self):
        ipython = get_ipython()
        ipython.magics_manager.register(self)

    async def _release(self):
        ipython = get_ipython()
        mgr = ipython.magics_manager

        for kind in magic_kinds:
            for key in self.magics[kind]:
                del mgr.magics[kind][key]
