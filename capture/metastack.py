import logging
from typing import List

from capture.base import PicklevisCapturer
from event import PicklevisEvent, PicklevisEventMetaStack, PicklevisEventSource


logger = logging.getLogger(__file__)


class MetastackCapture(PicklevisCapturer):
    def __init__(self) -> None:
        super().__init__()

    def precall(self, opcode, op_name, stack=None, metastack=None, memo=None, pos=0, *args, **kwargs) -> List[PicklevisEvent]:
        events = []

        if metastack is not None:
            if op_name == "APPENDS":
                logger.debug(f"Appending {len(metastack[-1])} items to list")
                events.append(
                    PicklevisEventMetaStack(
                        opcode,
                        datasource=PicklevisEventSource.METASTACK,
                        stack=list(reversed(stack)),
                        elements=metastack[-1],
                    ),
                )
            elif op_name == "SETITEMS":
                logger.debug(f"Setting {len(metastack[-1])} items to dict")
                events.append(
                    PicklevisEventMetaStack(
                        opcode,
                        datasource=PicklevisEventSource.METASTACK,
                        stack=list(reversed(stack)),
                        elements=metastack[-1],
                    ),
                )
            elif op_name == "ADDITEMS":
                logger.debug(f"Adding {len(metastack[-1])} items to dict")
                events.append(
                    PicklevisEventMetaStack(
                        opcode,
                        datasource=PicklevisEventSource.METASTACK,
                        stack=list(reversed(stack)),
                        elements=metastack[-1],
                    ),
                )

            elif op_name == "LIST":
                logger.debug(f"Creating a list with {len(metastack[-1])} items")
                events.append(
                    PicklevisEventMetaStack(
                        opcode,
                        datasource=PicklevisEventSource.METASTACK,
                        stack=list(reversed(stack)),
                        elements=metastack[-1],
                    ),
                )
            elif op_name == "INST":
                logger.debug(f"Creating an instance with {len(metastack[-1])} items")
                events.append(
                    PicklevisEventMetaStack(
                        opcode,
                        datasource=PicklevisEventSource.METASTACK,
                        stack=list(reversed(stack)),
                        elements=metastack[-1],
                    ),
                )
            elif op_name == "DICT":
                logger.debug(f"Creating a dict with {len(metastack[-1])} items")
                events.append(
                    PicklevisEventMetaStack(
                        opcode,
                        datasource=PicklevisEventSource.METASTACK,
                        stack=list(reversed(stack)),
                        elements=metastack[-1],
                    ),
                )
            elif op_name == "OBJ":
                logger.debug(f"Creating an object with {len(metastack[-1])} items")
                events.append(
                    PicklevisEventMetaStack(
                        opcode,
                        datasource=PicklevisEventSource.METASTACK,
                        stack=list(reversed(stack)),
                        elements=metastack[-1],
                    ),
                )
            elif op_name == "FROZENSET":
                logger.debug(f"Creating a frozen set with {len(metastack[-1])} items")
                events.append(
                    PicklevisEventMetaStack(
                        opcode,
                        datasource=PicklevisEventSource.METASTACK,
                        stack=list(reversed(stack)),
                        elements=metastack[-1],
                    ),
                )
            elif op_name == "TUPLE":
                logger.debug(f"Creating a tuple with {len(metastack[-1])} items")
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


    def postcall(self, opcode, op_name, stack=None, metastack=None, memo=None, pos=0, *args, **kwargs) -> List[PicklevisEvent]:
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
