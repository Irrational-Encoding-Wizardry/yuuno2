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
        if self.current_core is not None:
            await run_in_main_thread(self.current_core.deactivate)
            await self.comms.release()
            await self.current_core.release()

        self.current_core = await self.provider.get()
        await self.current_core.acquire()
        await run_in_main_thread(self.current_core.activate)
        register(self, self.current_core)

    async def _acquire(self):
        # Try to import VapourSynth.
        try:
            import vapoursynth
        except ImportError:
            raise Exception("Failed to import VapourSynth. Aborting.") from None

        # Debug magics
        mgs = DebugMagics(shell=self.shell)
        await mgs.acquire()
        register(self, mgs)

        # Preparing VSScript.
        from yuuno2.vapoursynth.vsscript.script import VSScriptProvider
        self.provider = VSScriptProvider()
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
