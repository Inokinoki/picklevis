from enum import Enum


class PicklevisEventType(Enum):
    GROUP = 0,
    INFO = 1,
    ERROR = 2,
    STACK = 3,
    METASTACK = 4,
    MEMO = 5,


class PicklevisEvent:
    def __init__(self, opcode, byte_count=0, offset=0, *arg, **kwarg):
        self.opcode = opcode
        self.offset = offset
        self.byte_count = byte_count
        self.type = PicklevisEventType.INFO


class PicklevisEventGroup(PicklevisEvent):
    def __init__(self, opcode, byte_count=0, offset=0, *arg, **kwarg) -> None:
        super().__init__(opcode, byte_count, offset, *arg, **kwarg)
        self.type = PicklevisEventType.GROUP
        self.events = []
