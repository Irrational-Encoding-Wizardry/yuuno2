from async_timeout import timeout


class timeout_context(object):

    def __init__(self, ctm, after: float):
        self.ctm = ctm
        self.after = after

    async def __aenter__(self):
        with timeout(self.after):
            return await self.ctm.__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        with timeout(self.after):
            return await self.ctm.__aexit__(exc_type, exc_val, exc_type)
