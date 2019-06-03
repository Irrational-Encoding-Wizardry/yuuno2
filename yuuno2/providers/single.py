from typing import NoReturn, Mapping, Any, Optional

from yuuno2.resource_manager import register
from yuuno2.script import Script, ScriptProvider


class SingleScriptProvider(ScriptProvider):

    def __init__(self, script: Script):
        self.script = script

    async def get(self, **params: Any) -> Optional[Script]:
        await self.ensure_acquired()
        return self.script

    async def _acquire(self) -> NoReturn:
        await self.script.acquire()
        register(self.script, self)

    async def _release(self) -> NoReturn:
        await self.script.release(force=False)
        self.script = None
