
class PicklevisEventType:
    GROUP = 0,
    INFO = 1,
    ERROR = 2,
    STACK = 3,
    METASTACK = 4,
    MEMO = 5,


class PicklevisEventSource:
    UNKNOWN = 1,
    STACK = 2,
    METASTACK = 3,
    MEMO = 4,


BYTE_COUNT_FULL_LINE = -1


class PicklevisEvent:
    def __init__(self, opcode, byte_count=0, offset=0, datasource=PicklevisEventSource.UNKNOWN, detail="", *arg, **kwarg):
        self.opcode = opcode
        self.offset = offset
        self.byte_count = byte_count
        self.type = PicklevisEventType.INFO
        self.datasource = datasource
        self.detail = detail


class PicklevisEventGroup(PicklevisEvent):
    def __init__(self, opcode, byte_count=0, offset=0, *arg, **kwarg):
        PicklevisEvent.__init__(self, opcode, byte_count, offset, *arg, **kwarg)
        self.type = PicklevisEventType.GROUP
        self.events = []


class PicklevisEventMemo(PicklevisEvent):
    def __init__(self, opcode, byte_count=0, offset=0, datasource=PicklevisEventSource.UNKNOWN, detail="", stack=None, touched_elements=None, *arg, **kwarg):
        PicklevisEvent.__init__(self, opcode, byte_count, offset, datasource, detail, *arg, **kwarg)
        self.type = PicklevisEventType.MEMO

        # Touched parts
        self.stack = stack
        self.elements = touched_elements


class PicklevisEventStack(PicklevisEvent):
    def __init__(self, opcode, byte_count=0, offset=0, datasource=PicklevisEventSource.UNKNOWN, detail="", stack=None, elements=None, *arg, **kwarg):
        PicklevisEvent.__init__(self, opcode, byte_count, offset, datasource, detail, *arg, **kwarg)
        self.type = PicklevisEventType.STACK

        # Touched parts
        self.stack = stack
        self.elements = elements


class PicklevisEventMetaStack(PicklevisEvent):
    def __init__(self, opcode, byte_count=0, offset=0, datasource=PicklevisEventSource.UNKNOWN, detail="", stack=None, elements=None, *arg, **kwarg):
        PicklevisEvent.__init__(self, opcode, byte_count, offset, datasource, detail, *arg, **kwarg)
        self.type = PicklevisEventType.METASTACK

        # Touched parts
        self.stack = stack
        self.meta_stack = elements
