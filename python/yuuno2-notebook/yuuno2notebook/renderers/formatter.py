from IPython import get_ipython

from yuuno2.resource_manager import Resource
from yuuno2.vapoursynth.clip import VapourSynthClip

from yuuno2notebook.utils import delay_call, run_in_main_thread
from yuuno2notebook.renderers.text import ClipDisplay as TextRenderer
from yuuno2notebook.renderers.image import ClipDisplay as ImageRenderer


class MimeBundle:

    def __init__(self):
        self.mimes = {}

    def add_mime(self, mimetype, data):
        self.mimes[mimetype] = data

    def _repr_mimebundle_(self, *args, **kwargs):
        return self.mimes


class Formatter(Resource):
    MIMES = {
        "text/plain": TextRenderer,
        "image/png": ImageRenderer
    }

    @property
    def _supported_types(self):
        import vapoursynth
        return [
            vapoursynth.VideoNode
        ]

    def __init__(self, env):
        self.env = env

    def display(self, obj, *args, **kwargs):
        return delay_call(self._display(obj))._repr_mimebundle_(*args, **kwargs)

    async def _display(self, obj):
        bundle = MimeBundle()
        async with VapourSynthClip(obj, script=self.env.current_core) as clip:
            for mime, renderer in Formatter.MIMES.items():
                rendered = await renderer(clip).display()
                if rendered is None: continue
                bundle.add_mime(mime, rendered)
        return bundle

    def _acquire_sync(self):
        ipy = get_ipython()
        for type in self._supported_types:
            ipy.display_formatter.mimebundle_formatter.for_type(type, self.display)

    def _release_sync(self):
        ipy = get_ipython()
        for type in self._supported_types:
            ipy.display_formatter.mimebundle_formatter.pop(type)

    async def _acquire(self):
        await run_in_main_thread(self._acquire_sync)

    async def _release(self):
        await run_in_main_thread(self._release_sync)