import logging

from capture.base import PicklevisCapturer
from event import PicklevisEventMemo, PicklevisEventSource
from capture.utils import copy_stack


logger = logging.getLogger(__file__)


class MemoCapture(PicklevisCapturer):
    def __init__(self):
        PicklevisCapturer.__init__(self)
        self.last_memo = None

        self.memo_getter = None
        self.memo_setter = None
        self.touched_key = None

    def precall(self, opcode, op_name, stack=None, metastack=None, memo=None, pos=0, *args, **kwargs):
        events = []

        if memo is not None:
            if op_name == "PUT" or op_name == "BINPUT" or op_name == "LONG_BINPUT":
                self.last_memo = memo
        return events

    def postcall(self, opcode, op_name, stack=None, metastack=None, memo=None, pos=0, *args, **kwargs):
        events = []

        if memo is not None:
            if op_name == "PUT" or op_name == "BINPUT" or op_name == "LONG_BINPUT":
                touched_key = None
                value = stack[-1]
                for k, v in memo.items():
                    if value == v:
                        touched_key = k
                        break
                logger.debug("Set {} from stack as {}".format(stack[-1], touched_key))
                s = copy_stack(stack)
                s.reverse()
                events.append(
                    PicklevisEventMemo(
                        opcode,
                        datasource=PicklevisEventSource.STACK,
                        stack=s,
                        touched_elements=[touched_key],
                    ),
                )
            elif op_name == "GET" or op_name == "BINGET" or op_name == "LONG_BINGET":
                touched_key = None
                value = stack[-1]
                for k, v in memo.items():
                    if value == v:
                        touched_key = k
                        break
                logger.debug("Get {} from stack as {}".format(stack[-1], touched_key))
                events.append(
                    PicklevisEventMemo(
                        opcode,
                        datasource=PicklevisEventSource.MEMO,
                        stack=list(reversed(copy_stack(stack))),
                        touched_elements=[stack[-1]],
                    ),
                )
            elif op_name == "MEMOIZE":
                logger.debug("Memorize {} from stack as {}".format(stack[-1], len(memo) - 1))
                s = copy_stack(stack)
                s.reverse()
                events.append(
                    PicklevisEventMemo(
                        opcode,
                        datasource=PicklevisEventSource.STACK,
                        stack=s,
                        touched_elements=[str(len(memo) - 1)],
                    ),
                )
        return events
