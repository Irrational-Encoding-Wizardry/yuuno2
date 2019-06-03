from typing import Union, TypeVar


T = TypeVar("T")


Buffer = Union[bytearray, memoryview]
ConfigTypes = Union[bytes, str, int, float, None]
