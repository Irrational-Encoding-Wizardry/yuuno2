from yuuno2.asyncutils import get_yuuno_loop, YuunoThread

import asyncio
import contextvars
from queue import Queue
from asyncio import wrap_future, run_coroutine_threadsafe, AbstractEventLoop, get_running_loop
from typing import Any, Callable, Awaitable, TypeVar, Optional, List
from concurrent.futures import Future as TFuture

T = TypeVar("T")


thr: Optional[YuunoThread] = None
main_thread_loop: Optional[AbstractEventLoop] = None

def _set_thread(thr_inst: Optional[YuunoThread]):
    global thr, main_thread_loop
    if thr is not None and thr_inst is not None:
        raise RuntimeError("Yuuno is already running.")

    main_thread_loop = get_running_loop()
    thr = thr_inst

def get_yuuno_thread() -> YuunoThread:
    if thr is None:
        raise RuntimeError("Yuuno is not running.")
    return thr

    
call_q: List[Queue] = []


def _insert_cb(cb):
    if cb is None:
        raise ValueError("The inserted callback may not be None.")
    if not call_q:
        if main_thread_loop is None:
            raise RuntimeError("There is no delayed call running right now.")
        main_thread_loop.call_soon_threadsafe(lambda: ctx.run(cb))
    else:
        call_q[-1].put_nowait(cb)


async def run_in_main_thread(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """
    Runs a function in the main loop and returns its result.
    """
    ctx = contextvars.copy_context()
    fut = TFuture()
    def _run():
        try:
            fut.set_result(func(*args, **kwargs))
        except Exception as e:
            fut.set_exception(e)
    _insert_cb(_run)
    
        
    return await wrap_future(fut)


def delay_call(coro) -> Any:
    """
    Delays a call and enables passing operations back to the main thread (which might have its own event-loop).
    """
    ctx = contextvars.copy_context()
    async def _run():
        return await ctx.run(get_running_loop().create_task, coro)

    q = Queue()
    call_q.append(q)

    try:
        fut = get_yuuno_thread().run_in_yuuno_loop(_run())
        fut.add_done_callback(lambda _: q.put(None))

        while (cb := q.get()) is not None:
            cb()

        return fut.result()
    finally:
        call_q.pop()

        # Drain the queue
        while not q.empty():
            next_cb = q.get()
            # Make sure the callbacks at least run!
            if not call_q and main_thread_loop is None:
                cb()
            else:
                # Move the callbacks one queue down
                _insert_cb(cb)
