##
# Stub for %load_ext yuuno
from IPython import InteractiveShell
from ipykernel.zmqshell import ZMQInteractiveShell

from yuuno2notebook.environment import Yuuno2Notebook
from yuuno2notebook.utils import delay_call


def load_ipython_extension(ipython: InteractiveShell) -> None:
    """
    Called when IPython load this extension.
    :param ipython:  The current IPython-console instance.
    """
    if not isinstance(ipython, ZMQInteractiveShell):
        raise EnvironmentError("Yuuno2 can only run from an IPython-Notebook.")

    environment = Yuuno2Notebook.instance(shell=ipython)
    if environment.shell != ipython or environment.acquired:
        raise EnvironmentError("Yuuno2 is already active.")

    delay_call(ipython, environment.acquire())


def unload_ipython_extension(ipython: InteractiveShell) -> None:
    """
    Called when IPython unloads the extension.
    """
    instance = Yuuno2Notebook.instance()
    if not instance.acquired:
        return

    delay_call(ipython, instance.release(force=True))
