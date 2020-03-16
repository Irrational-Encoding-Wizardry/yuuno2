import asyncio
import os
import sys
from typing import NoReturn, Mapping, Union, Any, Sequence

import aiorun

from yuuno2.clip import Clip
from yuuno2.networking.base import Connection
from yuuno2.providers.remote.server import RemoteScriptServer
from yuuno2.resource_manager import register

from yuuno2.script import Script, NOT_GIVEN, ScriptProvider
from yuuno2.typings import ConfigTypes
from yuuno2server.loops import install_event_loop
from yuuno2server.streams import FileInputStream, FileOutputStream

UNKNOWN = object()


class LocalScript(Script):

    def __init__(self, parent: Script):
        self.parent = parent

    def activate(self) -> NoReturn:
        self.parent.activate()

    def deactivate(self) -> NoReturn:
        self.parent.deactivate()

    async def set_config(self, key: str, value: ConfigTypes) -> NoReturn:
        full_key = key

        if key.startswith("subprocess."):
            key = key[len("subprocess."):]
            if key == "cd":
                os.chdir(value)
                return
            elif key.startswith("env."):
                key = key[4:]
                if value is None:
                    del os.environ[key]
                else:
                    os.environ[key] = str(value)
                return
            elif key == "pid":
                return

        await self.parent.set_config(full_key, value)

    async def get_config(self, key: str, default: Union[object, ConfigTypes] = NOT_GIVEN) -> ConfigTypes:
        full_key = key
        if key.startswith("subprocess."):
            key = key[len("subprocess."):]

            res = UNKNOWN

            if key.startswith("env."):
                res = os.environ.get(key[4:], default)
            elif key == "cd":
                res = os.getcwd()
            elif key == "pid":
                res = os.getpid()

            if res is NOT_GIVEN:
                raise KeyError(full_key)
            elif res is UNKNOWN:
                pass
            else:
                return res

        return await self.parent.get_config(full_key, default)

    async def list_config(self) -> Sequence[str]:
        return [
            "subprocess.cd",
            "subprocess.pid"
        ] + [
            f"subprocess.env.{k}"
            for k in os.environ.keys()
        ] + list(await self.parent.list_config())

    async def run(self, code: Union[bytes, str]) -> Any:
        return await self.parent.run(code)

    async def retrieve_clips(self) -> Mapping[str, Clip]:
        return await self.parent.retrieve_clips()

    async def _acquire(self) -> NoReturn:
        await self.parent.acquire()
        register(self.parent, self)

    async def _release(self) -> NoReturn:
        await self.parent.release(force=False)


if __name__ == "__main__":
    import click
    import importlib

    async def _run_with_provider(provider: ScriptProvider):
        async with provider:
            script = LocalScript(await provider.get())
            async with script:
                ingress = FileInputStream(sys.stdin.buffer)
                egress = FileOutputStream(sys.stdout.buffer)

                connection = Connection(ingress, egress)
                async with connection:
                    rss = RemoteScriptServer(script, connection)
                    async with rss:
                        print("Server is running...", file=sys.stderr)
                        while not ingress.is_closed():
                            await asyncio.sleep(0.1)

    @click.command()
    @click.option("--provider", help="Which script-provider should provide the script?", prompt=False)
    @click.option("--event-loop", default="default", help="The AsyncIO Event-Loop to be used.")
    def main(provider, event_loop):
        print("Initializing subprocess...", file=sys.stderr)
        module, variable = provider.split(":")
        mod = importlib.import_module(module)
        sp = getattr(mod, variable)()

        print("Spinning up event-loop", file=sys.stderr)
        install_event_loop(event_loop)
        loop = asyncio.get_event_loop()
        aiorun.run(_run_with_provider(sp), loop=loop)

        print("Exiting...", file=sys.stderr)

    main()
