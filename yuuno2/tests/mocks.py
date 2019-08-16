from typing import NoReturn, Union, Sequence, Any, Mapping, Optional

from yuuno2 import resource_manager, script
from yuuno2.clip import Clip, Frame
from yuuno2.format import RawFormat, Size, RGB24
from yuuno2.script import NOT_GIVEN, Script
from yuuno2.typings import ConfigTypes, Buffer


class MockResource(resource_manager.Resource):

    def __init__(self, name: str):
        self.name = name
        self.has_acquired = False
        self.has_released = False

    async def _acquire(self) -> NoReturn:
        self.has_acquired = True

    async def _release(self) -> NoReturn:
        self.has_released = True

    def __repr__(self):
        return f"<MockResource: {self.name}>"


class MockFrame(Frame):

    @property
    def size(self) -> Size:
        return Size(0, 0)

    @property
    def native_format(self) -> RawFormat:
        return RGB24

    async def can_render(self, format: RawFormat) -> bool:
        return format == RGB24

    async def render_into(self, buffer: Buffer, plane: int, format: RawFormat, offset: int = 0) -> int:
        return 0

    async def get_metadata(self) -> Mapping[str, Union[int, str, bytes]]:
        return {
            "id": id(self)
        }

    async def _acquire(self) -> NoReturn:
        pass

    async def _release(self) -> NoReturn:
        pass


class MockClip(Clip):

    def __getitem__(self, item) -> Frame:
        return MockFrame()

    async def _acquire(self) -> NoReturn:
        pass

    async def _release(self) -> NoReturn:
        pass

    async def get_metadata(self) -> Mapping[str, Union[int, str, bytes]]:
        return {
            "id": id(self)
        }


class MockScript(script.Script):

    def __init__(self, config=None):
        self.config = config or {}

    def activate(self) -> NoReturn:
        pass

    def deactivate(self) -> NoReturn:
        pass

    async def set_config(self, key: str, value: ConfigTypes) -> NoReturn:
        self.config[key] = value

    async def get_config(self, key: str, default: Union[object, ConfigTypes] = NOT_GIVEN) -> ConfigTypes:
        if key not in self.config:
            if default is NOT_GIVEN:
                raise KeyError(key)
            return default
        return self.config[key]

    async def list_config(self) -> Sequence[str]:
        return list(self.config)

    async def run(self, code: Union[bytes, str]) -> Any:
        self.config["last-command"] = code

    async def retrieve_clips(self) -> Mapping[str, Clip]:
        return {"test": MockClip()}

    async def _acquire(self) -> NoReturn:
        pass

    async def _release(self) -> NoReturn:
        pass


class MockScriptProvider(script.ScriptProvider):
    async def get(self, **params: Mapping[str, Any]) -> Optional[Script]:
        return MockScript(params)

    async def _acquire(self) -> NoReturn:
        pass

    async def _release(self) -> NoReturn:
        pass
