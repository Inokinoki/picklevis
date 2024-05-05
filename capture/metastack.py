import logging

from capture.base import PicklevisCapturer
from event import PicklevisEventMetaStack, PicklevisEventSource


logger = logging.getLogger(__file__)


class MetastackCapture(PicklevisCapturer):
    def __init__(self):
        PicklevisCapturer.__init__(self)

    def precall(self, opcode, op_name, stack=None, metastack=None, *args, **kwargs):
        events = []

        if metastack is not None:
            if op_name == "APPENDS":
                logger.debug("Appending {} items to list".format(len(metastack[-1])))
                events.append(
                    PicklevisEventMetaStack(
                        opcode,
                        datasource=PicklevisEventSource.METASTACK,
                        stack=list(reversed(stack)),
                        elements=metastack[-1],
                    ),
                )
            elif op_name == "SETITEMS":
                logger.debug("Setting {} items to dict".format(len(metastack[-1])))
                events.append(
                    PicklevisEventMetaStack(
                        opcode,
                        datasource=PicklevisEventSource.METASTACK,
                        stack=list(reversed(stack)),
                        elements=metastack[-1],
                    ),
                )
            elif op_name == "ADDITEMS":
                logger.debug("Adding {} items to dict".format(len(metastack[-1])))
                events.append(
                    PicklevisEventMetaStack(
                        opcode,
                        datasource=PicklevisEventSource.METASTACK,
                        stack=list(reversed(stack)),
                        elements=metastack[-1],
                    ),
                )

            elif op_name == "LIST":
                logger.debug("Creating a list with {} items".format(len(metastack[-1])))
                events.append(
                    PicklevisEventMetaStack(
                        opcode,
                        datasource=PicklevisEventSource.METASTACK,
                        stack=list(reversed(stack)),
                        elements=metastack[-1],
                    ),
                )
            elif op_name == "INST":
                logger.debug("Creating an instance with {} items".format(len(metastack[-1])))
                events.append(
                    PicklevisEventMetaStack(
                        opcode,
                        datasource=PicklevisEventSource.METASTACK,
                        stack=list(reversed(stack)),
                        elements=metastack[-1],
                    ),
                )
            elif op_name == "DICT":
                logger.debug("Creating a dict with {} items".format(len(metastack[-1])))
                events.append(
                    PicklevisEventMetaStack(
                        opcode,
                        datasource=PicklevisEventSource.METASTACK,
                        stack=list(reversed(stack)),
                        elements=metastack[-1],
                    ),
                )
            elif op_name == "OBJ":
                logger.debug("Creating an object with {} items".format(len(metastack[-1])))
                events.append(
                    PicklevisEventMetaStack(
                        opcode,
                        datasource=PicklevisEventSource.METASTACK,
                        stack=list(reversed(stack)),
                        elements=metastack[-1],
                    ),
                )
            elif op_name == "FROZENSET":
                logger.debug("Creating a frozen set with {} items".format(len(metastack[-1])))
                events.append(
                    PicklevisEventMetaStack(
                        opcode,
                        datasource=PicklevisEventSource.METASTACK,
                        stack=list(reversed(stack)),
                        elements=metastack[-1],
                    ),
                )
            elif op_name == "TUPLE":
                logger.debug("Creating a tuple with {} items".format(len(metastack[-1])))
                events.append(
                    PicklevisEventMetaStack(
                        opcode,
                        datasource=PicklevisEventSource.METASTACK,
                        stack=list(reversed(stack)),
                        elements=metastack[-1],
                    ),
                )

            elif op_name == "POP_MARK" and stack is None:
                logger.debug("Dropping the current meta stack and replace with")
                events.append(
                    PicklevisEventMetaStack(
                        opcode,
                        datasource=PicklevisEventSource.METASTACK,
                        stack=list(reversed(stack)),
                        elements=metastack[-1],
                    ),
                )
        return events


    def postcall(self, opcode, op_name, metastack=None, *args, **kwargs):
        events = []

        if op_name == "MARK" and metastack is not None:
            logger.debug("Pushed the current stack to metastack")
            events.append(
                PicklevisEventMetaStack(
                    opcode,
                    datasource=PicklevisEventSource.STACK,
                    elements=list(reversed(metastack[-1])),
                ),
            )
        return events
