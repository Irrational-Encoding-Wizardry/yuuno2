from IPython import InteractiveShell
from traitlets import Any
from traitlets.config import SingletonConfigurable, Instance

from yuuno2.resource_manager import NonAbcResource, register
from yuuno2.script import Script
from yuuno2notebook.control import ControlMagics
from yuuno2notebook.debug import DebugMagics
from yuuno2notebook.networking import JupyterCommManager
from yuuno2notebook.runvpy import RunVpyMagics


class Yuuno2Notebook(SingletonConfigurable, NonAbcResource):

    shell = Instance(InteractiveShell)
    provider = Any()
    current_core = Instance(Script, allow_none=True, default_value=None)

    comms = Instance(JupyterCommManager, allow_none=True, default_value=None)

    async def create_new_core(self):
        if self.current_core is not None:
            self.current_core.deactivate()
            await self.comms.release()
            await self.current_core.release()

        self.current_core = await self.provider.get()
        await self.current_core.acquire()
        self.current_core.activate()
        register(self, self.current_core)

        self.comms = JupyterCommManager(self.current_core)
        await self.comms.acquire()
        register(self, self.comms)

    async def _acquire(self):
        # Try to import VapourSynth.
        try:
            import vapoursynth
        except ImportError:
            raise Exception("Failed to import VapourSynth. Aborting.")

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

        # Push variables of core.
        self.shell.push({'vapoursynth': vapoursynth, 'core': vapoursynth.core})

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
