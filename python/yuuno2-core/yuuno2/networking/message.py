from typing import NamedTuple, Sequence, ByteString

from yuuno2.typings import JSON

class Message(NamedTuple):
    message: JSON
    data: Sequence[ByteString] = ()
