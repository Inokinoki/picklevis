import argparse
import io
import logging
import pickle
import pickletools
import platform
import sys

from capture.metastack import MetastackCapture
from capture.memo import MemoCapture
from capture.misc import MiscCapture
from capture.stack import StackCapture

from event import PicklevisEvent
from event import PicklevisEventGroup


logger = logging.getLogger(__file__)

try:
    OPCODES = pickle._Unpickler.dispatch.keys()
    OriginalUnpickler = pickle._Unpickler
except Exception:
    # Fallback
    OPCODES = pickle.Unpickler.dispatch.keys()
    OriginalUnpickler = pickle.Unpickler

OPCODE_NAME_MAPPING = {}        # A bytes (with only one byte) to opcode name string mapping
OPCODE_INT_NAME_MAPPING = {}    # An int to opcode name string mapping
pickle_objects_dict = pickle.__dict__
for k in pickle_objects_dict:
    pickle_object = pickle_objects_dict[k]
    if isinstance(pickle_object, bytes) and len(pickle_object) == 1:
        if pickle_object[0] in OPCODES:
            OPCODE_NAME_MAPPING[pickle_object] = k
            OPCODE_INT_NAME_MAPPING[ord(pickle_object)] = k


class Unpickler(OriginalUnpickler):

    def __init__(self, file, *args, **kwargs):
        OriginalUnpickler.__init__(self, file, *args, **kwargs)

        self.picklevis_opcodes = []
        self.picklevis_ops = []
        self.picklevis_byte_count = []
        self.picklevis_events = []
        self.parse_error = None
        self.parse_error = None
        self._file = file
        self._captures = [
            MetastackCapture(),
            MemoCapture(),
            StackCapture(),
            MiscCapture(),
        ]
        self.current_frame_offset = 0
        self.current_frame_size = 0

        # Patch for Python 2
        if not hasattr(self, "metastack"):
            self.metastack = None

        for opcode in OPCODES:
            self.dispatch[opcode] = self.inspect_dispatch(opcode, self.dispatch[opcode])

    def inspect_dispatch(self, opcode, func):
        def inspector(self, *args, **kwargs):
            logger.debug("Calling {} for opcode 0x{:02X}".format(func.__name__, ord(chr(opcode))))
            self.picklevis_ops.append(func.__name__)
            self.picklevis_opcodes.append(opcode)

            in_frame = False
            # Python 2 only supports til protocol 2: without frame support
            if platform.python_version_tuple()[0] != '2' and self._unframer is not None and self._unframer.current_frame is not None:
                in_frame = True

            events = PicklevisEventGroup(opcode)

            if not in_frame:
                before = self._file.tell()
            else:
                before = self._unframer.current_frame.tell()

            for capture in self._captures:
                events.events += capture.precall(opcode, OPCODE_INT_NAME_MAPPING[ord(chr(opcode))], stack=self.stack, metastack=self.metastack, memo=self.memo, pos=before)

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
            if platform.python_version_tuple()[0] != '2' and opcode == pickle.FRAME[0]:
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
                events.events += capture.postcall(opcode, OPCODE_INT_NAME_MAPPING[ord(chr(opcode))], stack=self.stack, metastack=self.metastack, memo=self.memo, pos=before)

            self.picklevis_events.append(events)

            if not in_frame:
                # Do not count in_frame to avoid duplicated count
                self.picklevis_byte_count.append(after - before + 1)    # Plus the opcode
            logger.debug("Read {} bytes in {}".format(after - before, func.__name__))

        return inspector

    def find_class(self, module_name, global_name):
        logger.debug("Finding {} in {}".format(global_name, module_name))
        return OriginalUnpickler.find_class(self, module_name, global_name)

    def get_events(self):
        # Wrapper for events, could have other events
        return self.picklevis_events

    def get_file(self):
        return self._file


class NonExecutingAnalyzer(object):
    """Parse pickle opcodes without running unpickling logic."""

    def __init__(self, file_or_bytes):
        if hasattr(file_or_bytes, "read"):
            raw = file_or_bytes.read()
        else:
            raw = file_or_bytes

        if not isinstance(raw, bytes):
            raise TypeError("pickle payload must be bytes")

        self._raw = raw
        self._file = io.BytesIO(raw)
        self.picklevis_opcodes = []
        self.picklevis_ops = []
        self.picklevis_byte_count = []
        self.picklevis_events = []

    @staticmethod
    def _opcode_to_int(code):
        if isinstance(code, int):
            return code
        if isinstance(code, bytes):
            return code[0]
        return ord(code)

    def load(self):
        op_items = []
        parse_error = None
        iterator = pickletools.genops(self._raw)
        while True:
            try:
                op_items.append(next(iterator))
            except StopIteration:
                break
            except Exception as exc:
                parse_error = exc
                break

        raw_len = len(self._raw)
        positions = [pos for _, _, pos in op_items]

        for index, (op, arg, pos) in enumerate(op_items):
            opcode = self._opcode_to_int(op.code)
            self.picklevis_opcodes.append(opcode)
            self.picklevis_ops.append(op.name)
            OPCODE_INT_NAME_MAPPING.setdefault(opcode, op.name)

            if index + 1 < len(positions):
                next_pos = positions[index + 1]
            else:
                next_pos = raw_len
            byte_count = max(1, next_pos - pos)
            self.picklevis_byte_count.append(byte_count)

            event = PicklevisEventGroup(opcode, byte_count=byte_count, offset=pos)
            if arg is not None:
                event.events.append(PicklevisEvent(opcode, detail=str(arg)))
            self.picklevis_events.append(event)

        if parse_error is not None:
            self.parse_error = str(parse_error)

    def get_events(self):
        return self.picklevis_events

    def get_file(self):
        self._file.seek(0)
        return self._file


def analyze_pickle_bytes(payload, execute=False):
    if execute:
        file_handle = io.BytesIO(payload)
        unpickler = Unpickler(file_handle)
        unpickler.load()
        return unpickler

    analyzer = NonExecutingAnalyzer(payload)
    analyzer.load()
    return analyzer


def analyze_pickle_file(path, execute=False):
    with open(path, "rb") as f:
        payload = f.read()
    return analyze_pickle_bytes(payload, execute=execute)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Visualize Python pickle files.")
    parser.add_argument("pickle_file", help="Path to a pickle file")
    parser.add_argument("-o", "--output", help="Output html file path")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Run pickle unpickling semantics (unsafe for untrusted files)",
    )
    parser.add_argument("--verbose", action="store_true", help="Print parsed opcodes")
    args = parser.parse_args(argv)

    unpickler = analyze_pickle_file(args.pickle_file, execute=args.execute)

    output_path = args.output or "{}.html".format(args.pickle_file)
    if args.verbose:
        for event in unpickler.picklevis_events:
            op_name = OPCODE_INT_NAME_MAPPING.get(event.opcode, "UNKNOWN")
            print("[{}] {} at {} with {} bytes".format(event.type, op_name, event.offset, event.byte_count))
    if getattr(unpickler, "parse_error", None):
        print("WARNING:\t{}".format(unpickler.parse_error))

    print("OPERATIONS:\t{}".format(len(unpickler.picklevis_ops)))
    print("OPCODES:\t{}".format(len(unpickler.picklevis_opcodes)))
    print("READ BYTES:\t{}".format(sum(unpickler.picklevis_byte_count)))
    print("Event groups: {}".format(len(unpickler.picklevis_events)))

    from render.html import render_to_html
    print(render_to_html(unpickler, output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
