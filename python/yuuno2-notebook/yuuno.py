##
# Stub for %load_ext yuuno
from IPython import InteractiveShell
from ipykernel.zmqshell import ZMQInteractiveShell

from yuuno2notebook.environment import Yuuno2Notebook
from yuuno2notebook.utils import get_yuuno_thread, _set_thread, delay_call
from yuuno2.asyncutils import YuunoThread


def _boot():
    yuuno_thread = YuunoThread()
    yuuno_thread.start_and_wait(5)
    _set_thread(yuuno_thread)

def _shutdown():
    get_yuuno_thread().close_and_wait(t)
    _set_thread(None)


def load_ipython_extension(ipython: InteractiveShell) -> None:
    """
    Called when IPython load this extension.
    :param ipython:  The current IPython-console instance.
    """
    environment = Yuuno2Notebook.instance(shell=ipython)
    if environment.shell != ipython or environment.acquired:
        raise EnvironmentError("Yuuno2 is already active.")

    _boot()
    delay_call(environment.acquire())


def unload_ipython_extension(ipython: InteractiveShell) -> None:
    """
    Called when IPython unloads the extension.
    """
    instance = Yuuno2Notebook.instance()
    if not instance.acquired:
        return

    delay_call(instance.release(force=True))
    _shutdown()