from abc import abstractmethod, ABC
from typing import Mapping, Union

from yuuno2.typings import Buffer
from yuuno2.format import Size, RawFormat, RGB24
from yuuno2.resource_manager import Resource


class MetadataContainer(ABC):

    @abstractmethod
    async def get_metadata(self) -> Mapping[str, Union[int, str, bytes]]:
        """
        Returns generic metadata about the frame.

        :return: A mapping of generic metadata.
        """
        return {}


class Frame(MetadataContainer, Resource, ABC):
    """
    This class represents a single frame out of a clip.

    A frame has two properties that can be accessed synchronously:

    1. It's size.
    2. It's metadata.
    """

    @property
    def native_format(self) -> RawFormat:
        """
        Returns the native format of the image.

        This format is guaranteed to be supported by the :func:`render`

        :return: A :class:`yuuno2.format.RawFormat`-instance.
        """
        return RGB24

    @property
    def size(self) -> Size:
        """
        Returns the size of the frame with no subsampling applied.

        :return: A size-object that returns the size of the frame.
        """
        return Size(0, 0)

    @abstractmethod
    async def can_render(self, format: RawFormat) -> bool:
        """
        Checks if the contents of the frame can be rendered in the given format.

        :param format: The format of the frame.
        :return: The native format of the frame.
        """
        return format == self.native_format

    @abstractmethod
    async def render_into(self, buffer: Buffer, plane: int, format: RawFormat, offset: int = 0) -> int:
        """
        Renders the plane of the frame into the given binary buffer.

        :param buffer: The buffer to render the image into.
        :param plane:  The plane to render.
        :param format: The format to render the frame in.
        :param offset: Where in the buffer should you start.

        :exception ValueError:   Thrown if the image cannot be converted to the given format.
        :exception IndexError:   Thrown if the requested plane is outside the plane range.
        :exception BufferError:  Thrown if the buffer is too small at the given offset.

        :return: The amount of bytes written to the binary buffer.
        """
        return 0


class Clip(Resource, MetadataContainer, ABC):
    """
    This class is the base-class for a clip.
    """

    def __len__(self) -> int:
        return 0

    def __getitem__(self, item) -> Frame:
        raise NotImplementedError