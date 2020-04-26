from typing import NoReturn, Mapping, Union, Any, Sequence, Optional

from yuuno2.clip import Clip
from yuuno2.resource_manager import register
from yuuno2.script import Script, NOT_GIVEN, ScriptProvider
from yuuno2.typings import ConfigTypes


class WrappedScript(Script):

    def __init__(self, script: Script):
        self.script = script

    def activate(self) -> NoReturn:
        self.script.activate()

    def deactivate(self) -> NoReturn:
        self.script.deactivate()

    async def set_config(self, key: str, value: ConfigTypes) -> NoReturn:
        await self.ensure_acquired()
        await self.script.set_config(key, value)

    async def get_config(self, key: str, default: Union[object, ConfigTypes] = NOT_GIVEN) -> ConfigTypes:
        await self.ensure_acquired()
        return await self.script.get_config(key, default, NOT_GIVEN)

    async def list_config(self) -> Sequence[str]:
        await self.ensure_acquired()
        return await self.script.list_config()

    async def run(self, code: Union[bytes, str]) -> Any:
        await self.ensure_acquired()
        return await self.script.run(code)

    async def retrieve_clips(self) -> Mapping[str, Clip]:
        await self.ensure_acquired()
        return await self.script.retrieve_clips()

    async def _acquire(self) -> NoReturn:
        await self.script.acquire()
        register(self.script, self)

    async def _release(self) -> NoReturn:
        await self.script.release(force=False)


class WrappedScriptProvider(ScriptProvider):

    def __init__(self, provider: ScriptProvider):
        self.provider = provider

    async def get(self, **params: Any) -> Optional[Script]:
        await self.ensure_acquired()
        return await self.provider.get(**params)

    async def list(self):
        await self.ensure_acquired()
        async for d in self.provider.list():
            yield d

    async def _acquire(self) -> NoReturn:
        await self.provider.acquire()
        register(self.provider, self)

    async def _release(self) -> NoReturn:
        await self.provider.release(force=False)