
from capture.base import PicklevisCapturer
from event import PicklevisEvent


class MiscCapture(PicklevisCapturer):
    def __init__(self):
        super().__init__()

    def precall(self, *args, **kwargs):
        return []

    def postcall(self, opcode, op_name, *args, **kwargs):
        events = []
        if op_name == "PROTO":
            events.append(
                PicklevisEvent(
                    opcode,
                    byte_count=1,
                    offset=1,
                    detail="Protocol version",
                )
            )
        return events
