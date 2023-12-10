from typing import List
from event import PicklevisEvent


class PicklevisCapturer:
    def __init__(self) -> None:
        pass

    def precall(self, opcode, op_name, stack=None, metastack=None, memo=None, pos=0, *args, **kwargs) -> List[PicklevisEvent]:
        ...

    def postcall(self, opcode, op_name, stack=None, metastack=None, memo=None, pos=0, *args, **kwargs) -> List[PicklevisEvent]:
        ...
