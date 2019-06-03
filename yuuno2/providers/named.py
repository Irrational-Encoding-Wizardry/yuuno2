from typing import NoReturn, Mapping, Any, Optional, MutableMapping

from yuuno2.resource_manager import register, on_release
from yuuno2.script import ScriptProvider, Script


class NamedScriptProvider(ScriptProvider):

    def __init__(self, parent: ScriptProvider):
        self.parent = parent

        self._scripts: MutableMapping[str, Script] = {}

    async def get(self, **params: Any) -> Optional[Script]:
        await self.ensure_acquired()

        name: Optional[str] = params.pop('name', None)
        if name is None:
            return await self.parent.get(**params)

        create: bool = params.pop('create', False)
        if name in self._scripts:
            return self._scripts[name]
        if not create:
            return None

        script = await self.parent.get(**params)
        register(self, script)
        self._scripts[name] = script
        on_release(script, lambda s: self._release_script(name))
        return script

    def _release_script(self, name: str):
        del self._scripts[name]

    async def _acquire(self) -> NoReturn:
        await self.parent.acquire()
        register(self.parent, self)

    async def _release(self) -> NoReturn:
        await self.parent.release(force=False)
        self.parent = None
