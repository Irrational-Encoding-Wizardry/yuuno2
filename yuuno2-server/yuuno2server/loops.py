from asyncio import set_event_loop


def install_event_loop(event_loop):
    if event_loop == "uvloop":
        import uvloop

        uvloop.install()
    elif event_loop == "iocp":
        from asyncio import ProactorEventLoop
        set_event_loop(ProactorEventLoop())

    else:
        pass
