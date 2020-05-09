from IPython import InteractiveShell
from traitlets import Any
from traitlets.config import SingletonConfigurable, Instance

from yuuno2.asyncutils import YuunoThread
from yuuno2.resource_manager import NonAbcResource, register
from yuuno2.script import Script

from yuuno2notebook.control import ControlMagics
from yuuno2notebook.debug import DebugMagics
from yuuno2notebook.runvpy import RunVpyMagics
from yuuno2notebook.utils import run_in_main_thread
from yuuno2notebook.renderers.formatter import Formatter


class Yuuno2Notebook(SingletonConfigurable, NonAbcResource):
    shell = Instance(InteractiveShell)
    provider = Any()
    current_core = Instance(Script, allow_none=True, default_value=None)

    async def create_new_core(self):
        self.current_core = await self.provider.get(default=True)

    async def _acquire(self):
        # Try to import VapourSynth.
        try:
            import vapoursynth
        except ImportError:
            raise ModuleNotFoundError("Failed to import VapourSynth. Aborting.") from None

        if not hasattr(vapoursynth, "has_policy"):
            raise ModuleNotFoundError("This VapourSynth is not supported. Please update your VapourSynth version to at least R51.")

        # Debug magics
        mgs = DebugMagics(shell=self.shell)
        await mgs.acquire()
        register(self, mgs)

        # Preparing VSScript.
        from yuuno2notebook.vscore import YuunoScriptProvider
        self.provider = YuunoScriptProvider()
        await self.provider.acquire()
        register(self, self.provider)
        await self.create_new_core()

        # Display-Formatters
        formatter = Formatter(self)
        await formatter.acquire()
        register(self, formatter)

        # Push variables of core.
        await run_in_main_thread(self.shell.push, {'vs': vapoursynth, 'vapoursynth': vapoursynth, 'core': vapoursynth.core})

        # Basic core configuration business
        control = ControlMagics(env=self)
        await control.acquire()
        register(self, control)

        # .vpy-execution
        vpy = RunVpyMagics(env=self)
        await vpy.acquire()
        register(self, vpy)

    async def _release(self):
        Yuuno2Notebook.clear_instance()
