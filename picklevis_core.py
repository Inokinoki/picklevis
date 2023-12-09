import pickle
from typing import Callable
import logging


logger = logging.getLogger(__file__)

OPCODES = pickle._Unpickler.dispatch.keys()

OPCODE_NAME_MAPPING = {}    # A bytes (with only one byte) to opcode name string mapping
pickle_objects_dict = pickle.__dict__
for k in pickle_objects_dict:
    pickle_object = pickle_objects_dict[k]
    if isinstance(pickle_object, bytes) and len(pickle_object) == 1:
        if int(pickle_object[0]) in OPCODES:
            OPCODE_NAME_MAPPING[pickle_object] = k


class Unpickler(pickle._Unpickler):

    def __init__(self, file, *args, **kwargs) -> None:
        super().__init__(file, *args, **kwargs)
        for opcode in OPCODES:
            self.dispatch[opcode] = self.inspect_dispatch(opcode, self.dispatch[opcode])

    def inspect_dispatch(self, opcode, func: Callable):
        def inspector(self, *args, **kwargs):
            logger.info(f"Calling {func.__name__} for opcode 0x{opcode:02x}")
            func(self, *args, **kwargs)

        return inspector


if __name__ == "__main__":
    with open("data.pkl", "rb") as f:
        Unpickler(f).load()
