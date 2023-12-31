import logging
from typing import List

from capture.base import PicklevisCapturer
from event import PicklevisEvent, PicklevisEventSource


logger = logging.getLogger(__file__)


class MemoCapture(PicklevisCapturer):
    def __init__(self) -> None:
        super().__init__()
        self.last_memo = None

        self.memo_getter = None
        self.memo_setter = None
        self.touched_key = None

    def precall(self, opcode, op_name, stack=None, metastack=None, memo=None, pos=0, *args, **kwargs) -> List[PicklevisEvent]:
        events = []

        if memo is not None:
            if op_name == "PUT" or op_name == "BINPUT" or op_name == "LONG_BINPUT":
                self.last_memo = memo
                events.append(
                    PicklevisEvent(opcode, byte_count=0, offset=0, datasource=PicklevisEventSource.MEMO),
                )
        return events

    def postcall(self, opcode, op_name, stack=None, metastack=None, memo=None, pos=0, *args, **kwargs) -> List[PicklevisEvent]:
        events = []

        if memo is not None:
            if op_name == "PUT" or op_name == "BINPUT" or op_name == "LONG_BINPUT":
                touched_key = None
                value = stack[-1]
                for k, v in memo.items():
                    if value == v:
                        touched_key = k
                        break
                logger.debug(f"Set {stack[-1]} from stack as {touched_key}")
                events.append(
                    PicklevisEvent(opcode, byte_count=0, offset=0, datasource=PicklevisEventSource.MEMO),
                )
            elif op_name == "GET" or op_name == "BINGET" or op_name == "LONG_BINGET":
                touched_key = None
                value = stack[-1]
                for k, v in memo.items():
                    if value == v:
                        touched_key = k
                        break
                logger.debug(f"Get {stack[-1]} from stack as {touched_key}")
                events.append(
                    PicklevisEvent(opcode, byte_count=0, offset=0, datasource=PicklevisEventSource.MEMO),
                )
            elif op_name == "MEMOIZE":
                logger.debug(f"Memorize {stack[-1]} from stack as {len(memo) - 1}")
                events.append(
                    PicklevisEvent(opcode, byte_count=0, offset=0, datasource=PicklevisEventSource.MEMO),
                )
        return events
