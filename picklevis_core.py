import pickle
from typing import Any, Callable
import logging

import sys

from capture.metastack import MetastackCapture
from capture.memo import MemoCapture
from capture.misc import MiscCapture
from capture.stack import StackCapture

from event import PicklevisEventGroup


logger = logging.getLogger(__file__)

OPCODES = pickle._Unpickler.dispatch.keys()

OPCODE_NAME_MAPPING = {}        # A bytes (with only one byte) to opcode name string mapping
OPCODE_INT_NAME_MAPPING = {}    # An int to opcode name string mapping
pickle_objects_dict = pickle.__dict__
for k in pickle_objects_dict:
    pickle_object = pickle_objects_dict[k]
    if isinstance(pickle_object, bytes) and len(pickle_object) == 1:
        if int(pickle_object[0]) in OPCODES:
            OPCODE_NAME_MAPPING[pickle_object] = k
            OPCODE_INT_NAME_MAPPING[int(pickle_object[0])] = k


class Unpickler(pickle._Unpickler):

    def __init__(self, file, *args, **kwargs) -> None:
        super().__init__(file, *args, **kwargs)

        self.picklevis_opcodes = []
        self.picklevis_ops = []
        self.picklevis_byte_count = []
        self.picklevis_events = []
        self._file = file
        self._captures = [
            MetastackCapture(),
            MemoCapture(),
            StackCapture(),
            MiscCapture(),
        ]
        self.current_frame_offset = 0
        self.current_frame_size = 0

        for opcode in OPCODES:
            self.dispatch[opcode] = self.inspect_dispatch(opcode, self.dispatch[opcode])

    def inspect_dispatch(self, opcode, func: Callable):
        def inspector(self, *args, **kwargs):
            logger.debug(f"Calling {func.__name__} for opcode 0x{opcode:02x}")
            self.picklevis_ops.append(func.__name__)
            self.picklevis_opcodes.append(opcode)

            in_frame = False
            if self._unframer is not None and self._unframer.current_frame is not None:
                in_frame = True

            events = PicklevisEventGroup(opcode)

            if not in_frame:
                before = self._file.tell()
            else:
                before = self._unframer.current_frame.tell()

            for capture in self._captures:
                events.events += capture.precall(opcode, OPCODE_INT_NAME_MAPPING[opcode], stack=self.stack, metastack=self.metastack, memo=self.memo, pos=before)

            # Call the real dispatch function
            try:
                func(self, *args, **kwargs)
            except Exception as e:
                if not in_frame:
                    after = self._file.tell()
                else:
                    after = self._unframer.current_frame.tell()

                # Update byte count
                events.byte_count = after - before + 1

                # Update offset in frame
                if in_frame:
                    events.offset = before - 1 + self.current_frame_offset
                else:
                    events.offset = before - 1

                self.picklevis_events.append(events)
                raise e

            if not in_frame:
                after = self._file.tell()
            else:
                after = self._unframer.current_frame.tell()

            # Update frame info
            if opcode == pickle.FRAME[0]:
                # Frame length is described in 8 bytes
                self.current_frame_offset = before + 8
                self.current_frame_size = after - before

            # Update byte count
            events.byte_count = after - before + 1

            # Update offset in frame
            if in_frame:
                events.offset = before - 1 + self.current_frame_offset
            else:
                events.offset = before - 1

            for capture in self._captures:
                events.events += capture.postcall(opcode, OPCODE_INT_NAME_MAPPING[opcode], stack=self.stack, metastack=self.metastack, memo=self.memo, pos=before)

            self.picklevis_events.append(events)

            if not in_frame:
                # Do not count in_frame to avoid duplicated count
                self.picklevis_byte_count.append(after - before + 1)    # Plus the opcode
            logger.debug(f"Read {after - before} bytes in {func.__name__}")

        return inspector

    def find_class(self, module_name: str, global_name: str) -> Any:
        logger.debug(f"Finding {global_name} in {module_name}")
        return super().find_class(module_name, global_name)

    def get_events(self):
        # Wrapper for events, could have other events
        return self.picklevis_events

    def get_file(self):
        return self._file


if __name__ == "__main__":
    with open("data.pkl", "rb") as f:
        unpickler = Unpickler(f)
        unpickler.load()
        print(f"OPERATIONS:\t{len(unpickler.picklevis_ops)}")
        print(f"OPCODES:\t{len(unpickler.picklevis_opcodes)}")
        print(f"READ BYTES:\t{sum(unpickler.picklevis_byte_count)}")
        print(f"Event groups: {len(unpickler.picklevis_events)}")
        if "--verbose" in sys.argv:
            for event in unpickler.picklevis_events:
                print(f"[{event.type.name}] {OPCODE_INT_NAME_MAPPING[event.opcode]} at {event.offset} with {event.byte_count} bytes")

        from render.html import render_to_html
        print(render_to_html(unpickler, "data.pkl.html"))
