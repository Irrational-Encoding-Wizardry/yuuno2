from typing import Any

from IPython.core.magic import magics_class

from yuuno2notebook.magic_base import ResourceMagics, line_magic, as_async_command

from yuuno2.resource_manager import _resources, ResourceProxy


def _repr(obj: Any) -> str:
    return (
        repr(obj)
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("<", "\\<")
        .replace(">", "\\>")
        .replace('"', '\\"')
        .replace("'", "\\'")
    )


@magics_class
class DebugMagics(ResourceMagics):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @line_magic
    @as_async_command
    def debug_y2_res(self, _):
        print("digraph {")
        for resource, state in _resources.items():
            rsid = f"obj{id(resource)}"
            o_repr = _repr(resource)
            o_type = "N"
            color = "black"

            if isinstance(resource, ResourceProxy):
                target = resource.target()
                o_repr = _repr(target)
                o_type = "P"

            if state.released:
                color = "red"

            print(f'  "{rsid}" [shape=record,label="{o_type} | {o_repr} | {state.acquired}",color={color}]')
            for child in state.children:
                print(f'  "{rsid}" -> "obj{id(child)}" [dir=back]')

        print("}")