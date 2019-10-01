from IPython.core.magic import magics_class, line_magic
from traitlets import Any

from yuuno2.script import Script
from yuuno2notebook.magic_base import ResourceMagics, as_async_command


@magics_class
class ControlMagics(ResourceMagics):

    env = Any()

    @line_magic
    @as_async_command
    async def script_config(self, line):
        name, *op = line.split(" ", 3)
        if name == "get":
            if len(op) != 1:
                print("%script_config get [key]")
                return

            key, *_ = op

            script: Script = self.env.current_core
            print(repr(await script.get_config(key, None)))
        elif name == "set":
            if len(op) != 2:
                print("%script_config set [key] [value]")
                return

            key, raw_value = op
            value = eval(raw_value)
            script: Script = self.env.current_core
            await script.set_config(key, value)
            print("Config updated.")

        elif name == "list":
            script: Script = self.env.current_core
            keys = list(await script.list_config())
            print("Configuration:")
            for key in keys:
                print(">", key)

        else:
            print("%script_config get [key]")
            print("%script_config set [key] [value]")
            print("%script_config list [key]")

    @line_magic
    @as_async_command
    async def reset_core(self, _):
        await self.env.create_new_core()
        print("Core reset.")