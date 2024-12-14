import logging

from capture.base import PicklevisCapturer
from event import PicklevisEventSource, PicklevisEventStack
from capture.utils import copy_stack


logger = logging.getLogger(__file__)


class StackCapture(PicklevisCapturer):
    def __init__(self):
        PicklevisCapturer.__init__(self)
        self.temp = []

    def precall(self, opcode, op_name, stack=None, *args, **kwargs):
        if stack is None:
            return []

        events = []

        if op_name == "STOP":
            logger.debug("Stopping with {} as return value".format(stack[-1]))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.STACK,
                    stack=list(reversed(copy_stack(stack[:-1]))),
                    elements=[stack[-1]],
                ),
            )
        elif op_name == "BUILD":
            logger.debug("Building {} with {} (__setstate__/__dict__/setattr)".format(stack[-2], stack[-1]))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.UNKNOWN,
                    stack=list(reversed(copy_stack(stack[:-1]))),
                    elements=[stack[-1]],
                ),
            )
        elif op_name == "SETITEM":
            logger.debug("Setting {} with {}: {}".format(stack[-3], stack[-2], stack[-1]))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.UNKNOWN,
                    stack=list(reversed(copy_stack(stack[:-2]))),
                    elements=["{}: {}".format(stack[-2], stack[-1])],
                ),
            )
        elif op_name == "APPEND":
            logger.debug("Appending {} to {}".format(stack[-1], stack[-2]))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.UNKNOWN,
                    stack=list(reversed(copy_stack(stack[:-1]))),
                    elements=[stack[-1]],
                ),
            )
        elif op_name == "POP":
            logger.debug("Dropping {}".format(stack[-1]))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.STACK,
                    stack=list(reversed(copy_stack(stack[:-1]))),
                    elements=[stack[-1]],
                ),
            )
        elif op_name == "REDUCE":
            logger.debug("Reducing {} with {}".format(stack[-2], stack[-1]))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.UNKNOWN,
                    stack=list(reversed(copy_stack(stack[:-1]))),
                    elements=[stack[-1]],
                ),
            )
        elif op_name == "DUP":
            logger.debug("Duplicating {}".format(stack[-1]))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.UNKNOWN,
                    stack=list(reversed(copy_stack(stack))),
                    elements=[stack[-1]],
                ),
            )
        elif op_name == "EXT1" or op_name == "EXT2" or op_name == "EXT4":
            logger.debug("Loading extension {}".format(stack[-1]))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.STACK,
                    stack=list(reversed(copy_stack(stack))),
                ),
            )
        elif op_name == "STACK_GLOBAL":
            logger.debug("Loading class {} from {}".format(stack[-1], stack[-2]))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.UNKNOWN,
                    stack=list(reversed(copy_stack(stack[:-1]))),
                    elements=[stack[-1]],
                ),
            )
        elif op_name == "NEWOBJ_EX":
            self.temp.append(stack[-3])
            self.temp.append(stack[-2])
            self.temp.append(stack[-1])
            logger.debug("Loading class {} with {} and {}".format(stack[-3], stack[-2], stack[-1]))
        elif op_name == "NEWOBJ":
            self.temp.append(stack[-2])
            self.temp.append(stack[-1])
            logger.debug("Loading class {} with {}".format(stack[-2], stack[-1]))
        elif op_name == "TUPLE3":
            self.temp.append(stack[-3])
            self.temp.append(stack[-2])
            self.temp.append(stack[-1])
            logger.debug("Loading tuple {}".format(self.temp))
        elif op_name == "TUPLE2":
            self.temp.append(stack[-2])
            self.temp.append(stack[-1])
            logger.debug("Loading tuple {}".format(self.temp))
        elif op_name == "TUPLE1":
            self.temp.append(stack[-1])
            logger.debug("Loading tuple {}".format(self.temp))
        elif op_name == "BINPERSID":
            logger.debug("Loading persistent {}".format(stack[-1]))
            events.append(
                PicklevisEvent(opcode, byte_count=0, offset=0, datasource=PicklevisEventSource.STACK),
            )
        return events

    def postcall(self, opcode, op_name, stack=None, *args, **kwargs):
        if stack is None:
            return []

        events = []

        if op_name == "GLOBAL":
            klass = stack[-1]
            klass_name = str(klass)
            if hasattr(op_name, "__name__"):
                klass_name = klass.__name__
            logger.debug("Loaded class {}".format(klass_name))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.UNKNOWN,
                    stack=list(reversed(copy_stack(stack[:-1]))),
                    elements=[klass_name],
                ),
            )
        elif op_name == "NEWOBJ_EX":
            logger.debug("Loaded class {} with {} and {} as {}".format(self.temp[-3], self.temp[-2], self.temp[-1], stack[-1]))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.UNKNOWN,
                    stack=list(reversed(copy_stack(stack))),
                    elements=self.temp,
                ),
            )
            self.temp.clear()
        elif op_name == "NEWOBJ":
            logger.debug("Loaded class {} with {} as {}".format(self.temp[-2], self.temp[-1], stack[-1]))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.UNKNOWN,
                    stack=list(reversed(copy_stack(stack))),
                    elements=self.temp.copy(),
                ),
            )
            self.temp.clear()
        elif op_name == "EMPTY_SET" or op_name == "EMPTY_DICT" or op_name == "EMPTY_LIST" or op_name == "EMPTY_TUPLE":
            logger.debug("Loaded empty {} {}".format(stack[-1].__class__.__name__, stack[-1]))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.UNKNOWN,
                    stack=list(reversed(copy_stack(stack[:-1]))),
                    elements=["Empty {}".format(stack[-1].__class__.__name__)],
                ),
            )
        elif op_name == "TUPLE3" or op_name == "TUPLE2" or op_name == "TUPLE1":
            logger.debug("Loaded tuple {}: {}".format(stack[-1], self.temp))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.UNKNOWN,
                    stack=list(reversed(copy_stack(stack))),
                    elements=self.temp.copy(),
                ),
            )
            self.temp.clear()
        elif op_name == "PERSID":
            logger.debug("Loaded persistent {}".format(stack[-1]))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.UNKNOWN,
                    stack=list(reversed(copy_stack(stack[:-1]))),
                    elements=[stack[-1]],
                ),
            )
        elif op_name == "NONE":
            logger.debug("Loaded None")
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.UNKNOWN,
                    stack=list(reversed(copy_stack(stack[:-1]))),
                    elements=["None"],
                ),
            )
        elif op_name == "NEWFALSE" or op_name == "NEWTRUE":
            logger.debug("Loaded bool {}".format(stack[-1]))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.UNKNOWN,
                    stack=list(reversed(copy_stack(stack[:-1]))),
                    elements=[str(stack[-1])],
                ),
            )
        elif op_name == "INT" or op_name == "BININT" or op_name == "BININT1" or op_name == "BININT2":
            logger.debug("Loaded int {}".format(stack[-1]))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.UNKNOWN,
                    stack=list(reversed(copy_stack(stack[:-1]))),
                    elements=[stack[-1]],
                ),
            )
        elif op_name == "LONG" or op_name == "LONG1" or op_name == "LONG4":
            logger.debug("Loaded long {}".format(stack[-1]))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.UNKNOWN,
                    stack=list(reversed(copy_stack(stack[:-1]))),
                    elements=[stack[-1]],
                ),
            )
        elif op_name == "FLOAT" or op_name == "BINFLOAT":
            logger.debug("Loaded float {}".format(stack[-1]))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.UNKNOWN,
                    stack=list(reversed(copy_stack(stack[:-1]))),
                    elements=[stack[-1]],
                ),
            )
        elif op_name == "STRING" or op_name == "BINSTRING" or\
            op_name == "UNICODE" or op_name == "BINUNICODE" or op_name == "BINUNICODE8" or\
            op_name == "SHORT_BINUNICODE" or op_name == "SHORT_BINSTRING":
            logger.debug("Loaded string {}".format(stack[-1]))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.UNKNOWN,
                    stack=list(reversed(copy_stack(stack[:-1]))),
                    elements=[stack[-1]],
                ),
            )
        elif op_name == "BINBYTES" or op_name == "BINBYTES8" or op_name == "BYTEARRAY8" or op_name == "SHORT_BINBYTES":
            logger.debug("Loaded bytes {}".format(stack[-1]))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.UNKNOWN,
                    stack=list(reversed(copy_stack(stack[:-1]))),
                    elements=[stack[-1]],
                ),
            )
        elif op_name == "NEXT_BUFFER":
            logger.debug("Loaded buffer {}".format(stack[-1]))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.UNKNOWN,
                    stack=list(reversed(copy_stack(stack[:-1]))),
                    elements=[stack[-1]],
                ),
            )
        elif op_name == "READONLY_BUFFER":
            logger.debug("Made buffer {} readonly".format(stack[-1]))
            events.append(
                PicklevisEventStack(
                    opcode,
                    datasource=PicklevisEventSource.UNKNOWN,
                    stack=list(reversed(copy_stack(stack))),
                    elements=["Read-only"],
                ),
            )
        return events
