import sys
import math
import shutil
from typing import Optional

import asyncio
from blessed import Terminal
from IPython import get_ipython

from yuuno2.format import Size, RawFormat, ColorFamily, SampleType, RGB24, GRAY8
from yuuno2notebook.utils import delay_call


def clamp(value, min, max):
    if value < min:
        return min
    elif value > max:
        return max
    else:
        return value


def remap(value, min_old, max_old, min_new, max_new):
    max_old -= min_old
    max_new -= min_new
    value = clamp(value - min_old, 0, max_old)
    conv_value = max_old / max_new
    value = clamp(int(round(value / conv_value)), 0, max_new)
    return value + min_new


class Renderer:
    
    def format(self) -> Optional[RawFormat]:
        raise NotImplementedError()

    def size(self) -> Optional[Size]:
        return None

    def render(self, sz_in: Size, *planes: bytes) -> str:
        raise NotImplementedError()


class DataRenderer(Renderer):

    def format(self):
        return None

    def size(self) -> Optional[Size]:
        return None

    def render(self, clip, frame):
        return f"<Clip width={size.width} height={size.height} {len(self.clip)} frames>"


class AsciiRenderer(Renderer):

    def __init__(self, palette="@ ", target_size=Size(80, 60), prefix="", postfix=""):
        self.palette = palette
        self.target_size = target_size
        self.prefix = prefix
        self.postfix = postfix

    def format(self) -> RawFormat:
        return GRAY8

    def size(self) -> Optional[Size]:
        return Size(self.target_size.width, self.target_size.height)

    def render(self, sz_in: Size, plane_g) -> str:
        target_sz = self.target_size
        if sz_in.width <= self.target_size.width and sz_in.height <= self.target_size.height:
            target_sz = sz_in

        out = [[" "]*target_sz.width for _ in range(target_sz.height)]
        for oy in range(sz_in.height):
            sy = remap(oy, 0, sz_in.height, 0, target_sz.height)
            offset = oy*sz_in.width
            for ox in range(sz_in.width):
                sx = remap(ox, 0, sz_in.width, 0, target_sz.width)
                v = remap(plane_g[offset + ox], 0, 256, 0, len(self.palette)-1)
                out[sy][sx] = self.palette[v]

        return self.prefix + "\n".join("".join(v) for v in out) + self.postfix


class SingleLineANSIRenderer(Renderer):
    def __init__(self, terminal: Terminal):
        self.terminal = terminal

    def format(self) -> RawFormat:
        return RGB24

    def size(self) -> Size:
        return Size(self.terminal.width, self.terminal.height - 4)

    def render(self, sz_in: Size, plane_r: bytes, plane_g: bytes, plane_b: bytes) -> str:
        target_sz = self.size()
        if sz_in.width <= target_sz.width and sz_in.height <= target_sz.height:
            target_sz = sz_in

        out = [[" "]*target_sz.width for _ in range(target_sz.height)]
        pixels = tuple(zip(plane_r, plane_g, plane_b))
        for sy in range(target_sz.height):
            oy = remap(sy, 0, target_sz.height, 0, sz_in.height)
            for sx in range(target_sz.width):
                ox = remap(sx, 0, target_sz.width, 0, sz_in.width)
                out[sy][sx] = f"{self.terminal.on_color_rgb(*pixels[oy*sz_in.width + ox])} "

        out[-1].append(self.terminal.normal)
        return f"{self.terminal.normal}\n".join("".join(p) for p in out)


class MultiLineANSIRenderer(Renderer):
    def __init__(self, terminal: Terminal):
        self.terminal = terminal

    def format(self) -> RawFormat:
        return RGB24

    def size(self) -> Size:
        return Size(self.terminal.width, (self.terminal.height - 3)*2)

    def render(self, sz_in: Size, plane_r: bytes, plane_g: bytes, plane_b: bytes) -> str:
        target_sz = self.size()
        if sz_in.width <= target_sz.width and sz_in.height <= target_sz.height:
            target_sz = sz_in

        lines = math.ceil(target_sz.height/2)
        out = [[" "]*target_sz.width for _ in range(lines)]
        pixels = tuple(zip(plane_r, plane_g, plane_b))
        for sy in range(lines):
            oyt = remap(sy*2, 0, target_sz.height, 0, sz_in.height)
            oyb = None
            if sy+1 < lines:
                oyb = remap(sy*2+1, 0, target_sz.height, 0, sz_in.height)

            for sx in range(target_sz.width):
                ox = remap(sx, 0, target_sz.width, 0, sz_in.width)

                top = pixels[oyt*sz_in.width + ox]
                bottom = None
                if oyb is not None:
                    bottom = pixels[oyb*sz_in.width + ox]

                top = self.terminal.color_rgb(*top)
                bottom = self.terminal.normal if bottom is None else self.terminal.on_color_rgb(*bottom)
                out[sy][sx] = f"{bottom}{top}\u2580"

        out[-1].append(self.terminal.normal)
        return f"{self.terminal.normal}\n".join("".join(p) for p in out)


class AutoSz:
    def get_tsz(self):
        return shutil.get_terminal_size((80, 60))

    @property
    def width(self):
        return self.get_tsz().columns-5

    @property
    def height(self):
        return self.get_tsz().lines-2


def _get_correct_renderer():
    shell = get_ipython().__class__.__name__
    if shell in ("NoneType", "TerminalInteractiveShell"):
        can_do_unicode = "\u2580".encode(sys.stdout.encoding, errors="replace").decode(sys.stdout.encoding) == "\u2580"
        term = Terminal()
        if term.is_a_tty and term.does_styling and term.number_of_colors > 0:
            if can_do_unicode:
                return MultiLineANSIRenderer(term)
            else:
                return SingleLineANSIRenderer(term)
        elif can_do_unicode:
            return AsciiRenderer("\u2588@%#*+=-:. ", target_size=AutoSz())

    return AsciiRenderer("@%#*+=-:. ", target_size=AutoSz())
renderer = _get_correct_renderer()


class ClipDisplay:

    def __init__(self, clip):
        self.clip = clip

    async def display(self):
        async with self.clip[0] as frame:
            if not await frame.can_render(renderer.format()):
                return await self._display_unsupported(frame)
            else:
                return await self._display_renderable(frame)

    async def _display_unsupported(self, frame):
        size = frame.size
        return f"<Clip width={size.width} height={size.height} {len(self.clip)} frames>"

    async def _display_renderable(self, frame):
        size = frame.size
        desired = renderer.size()
        ar_f = size.width/size.height
        ar_d = desired.width/desired.height

        if ar_f < ar_d:
            factor = desired.height / size.height
        elif ar_f > ar_d:
            factor = desired.width / size.width

        target = Size(width=round(size.width*factor), height=round(size.height*factor))
        try:
            clip = await self.clip.resize(target)
        except Exception as e:
            # return await self._display_unsupported(frame)
            raise

        async with clip:
            async with clip[0] as frame:
                format = renderer.format()
                planes = [bytearray(format.get_plane_size(i, target)) for i in range(format.num_planes)]
                await asyncio.gather(*(frame.render_into(planes[i], i, format, 0) for i in range(format.num_planes)))
        return renderer.render(target, *planes)
