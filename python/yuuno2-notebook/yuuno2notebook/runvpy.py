import sys
import runpy
import types
from contextlib import contextmanager

from IPython.core.magic import line_cell_magic, line_magic, magics_class
from traitlets import Any

from yuuno2notebook.magic_base import ResourceMagics


NOT_GIVEN = object()


@contextmanager
def pristine_outputs():
    from vapoursynth import get_outputs, clear_outputs

    previous_outputs = dict(get_outputs())
    clear_outputs()

    results = {}

    try:
        yield results
    except:                                               # Bare-Except required by syntax.
        raise
    else:
        results.update(get_outputs())
    finally:
        clear_outputs()
        for oid, oclip in previous_outputs.items():
            oclip.set_output(oid)


@contextmanager
def temporary_module(module: types.ModuleType):
    name = module.__name__
    old = sys.modules.get(name, NOT_GIVEN)
    sys.modules[name] = module
    try:
        yield name.__dict__
    finally:
        if old is not NOT_GIVEN:
            sys.modules[name] = old


@magics_class
class RunVpyMagics(ResourceMagics):

    env = Any()

    @line_magic
    def execvpy(self, line):
        runpy.run_path(line, {}, "__vapoursynth__")

    @line_cell_magic
    def runvpy(self, line, cell):
        if cell is None:
            return self.runvpy__line(line)
        else:
            return self.runvpy__cell(line, cell)

    def runvpy__line(self, line):
        with pristine_outputs() as result:
            self.execvpy(line)
        return result

    def runvpy__cell(self, line, cell):
        param = line.split(" ")[0]
        module = types.ModuleType("__vapoursynth__")
        compiled = compile(cell, filename="<yuuno2:vpy>", mode="exec")

        with pristine_outputs() as result:
            with temporary_module(module):
                exec(compiled, module.__dict__, module.__dict__)

        self.env.shell.push({param: result})
