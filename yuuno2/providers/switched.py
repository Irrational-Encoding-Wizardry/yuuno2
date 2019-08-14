from typing import NoReturn, Mapping, Any, Optional

from yuuno2.resource_manager import register
from yuuno2.script import ScriptProvider, Script


class SwitchedScriptProvider(ScriptProvider):

    def __init__(self, _switch: str = "type", **parents: ScriptProvider):
        self._switch = _switch
        self.parents = parents

    async def get(self, **params: Any) -> Optional[Script]:
        if self._switch not in params:
            return

        stype = params.pop(self._switch)
        if stype not in self.parents:
            return None

        return (await self.parents[stype].get(**params))

    async def _acquire(self) -> NoReturn:
        for parent in self.parents.values():
            await parent.acquire()
            register(parent, self)

    async def _release(self) -> NoReturn:
        for parent in self.parents.values():
            await parent.release(force=False)
