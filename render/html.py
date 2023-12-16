
from event import PicklevisEventType, PicklevisEventSource, PicklevisEventGroup, PicklevisEvent
from picklevis_core import Unpickler, OPCODE_INT_NAME_MAPPING


def render_to_html(unpickler: Unpickler, name):
    i = 0
    with open(name, "w") as f:
        pkl_file = unpickler.get_file()
        for event in unpickler.get_events():
            if pkl_file.seek(event.offset) == event.offset:
                content = pkl_file.read(event.byte_count)
                f.write(f"[OP-{OPCODE_INT_NAME_MAPPING[event.opcode]}] {event.opcode}, {event.byte_count} bytes - {event.offset}: {content} <br/>")
        print(i)
    return i
