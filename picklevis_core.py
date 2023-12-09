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

        self.picklevis_ops = []
        self.picklevis_byte_count = []
        self._file = file

        for opcode in OPCODES:
            self.dispatch[opcode] = self.inspect_dispatch(opcode, self.dispatch[opcode])

    def inspect_dispatch(self, opcode, func: Callable):
        def inspector(self, *args, **kwargs):
            logger.debug(f"Calling {func.__name__} for opcode 0x{opcode:02x}")
            self.picklevis_ops.append(func.__name__)

            in_frame = False
            if self._unframer is not None and self._unframer.current_frame is not None:
                in_frame = True

            if not in_frame:
                before = self._file.tell()
            else:
                before = self._unframer.current_frame.tell()

            # Call the real dispatch function
            func(self, *args, **kwargs)

            if not in_frame:
                after = self._file.tell()
            else:
                after = self._unframer.current_frame.tell()

            if not in_frame:
                # Do not count in_frame to avoid duplicated count
                self.picklevis_byte_count.append(after - before + 1)    # Plus the opcode
            logger.debug(f"Read {after - before} bytes in {func.__name__}")

        return inspector


if __name__ == "__main__":
    with open("data.pkl", "rb") as f:
        unpickler = Unpickler(f)
        unpickler.load()
        print(f"OPCODES:\t{len(unpickler.picklevis_ops)}")
        print(f"READ BYTES:\t{sum(unpickler.picklevis_byte_count)}")

