from typing import NoReturn, Mapping, Any, Optional

from yuuno2.resource_manager import register
from yuuno2.script import ScriptProvider, Script
from yuuno2.vapoursynth.script import VapourSynthScript
from yuuno2.vapoursynth.vsscript.vs_capi import ScriptEnvironment
from yuuno2.vapoursynth.vsscript.vs_capi import enable_vsscript, disable_vsscript


class VSScript(VapourSynthScript):

    def __init__(self, provider: ScriptProvider):
        self.provider = provider
        # noinspection PyTypeChecker
        super().__init__(None)

    async def _acquire(self) -> NoReturn:
        register(self.provider, self)
        self.script_environment = ScriptEnvironment()
        self.script_environment.enable()

        self.environment = self.script_environment.environment()
        await super()._acquire()

    async def _release(self) -> NoReturn:
        await super()._release()
        if self.script_environment is not None:
            self.script_environment.dispose()
            self.script_environment = None
            self.environment = None


_counter = 0


class VSScriptProvider(ScriptProvider):
    async def get(self, **params: Any) -> Optional[Script]:
        return VSScript(self)

    async def _acquire(self) -> NoReturn:
        global _counter
        if _counter == 0:
            enable_vsscript()
        _counter += 1

    async def _release(self) -> NoReturn:
        global _counter
        _counter -= 1
        if _counter == 0:
            disable_vsscript()
