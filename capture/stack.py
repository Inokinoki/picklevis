import logging

from capture.base import PicklevisCapturer


logger = logging.getLogger(__file__)


class StackCapture(PicklevisCapturer):
    def __init__(self) -> None:
        super().__init__()
        self.temp = []

    def precall(self, op_name, stack=None, metastack=None, memo=None, pos=0, *args, **kwargs):
        if stack is None:
            return

        if op_name == "STOP":
            logger.debug(f"Stopping with {stack[-1]} as return value")
        elif op_name == "BUILD":
            logger.debug(f"Building {stack[-2]} with {stack[-1]} (__setstate__/__dict__/setattr)")
        elif op_name == "SETITEM":
            logger.debug(f"Setting {stack[-3]} with {stack[-2]}: {stack[-1]}")
        elif op_name == "APPEND":
            logger.debug(f"Appending {stack[-1]} to {stack[-2]}")
        elif op_name == "POP":
            logger.debug(f"Dropping {stack[-1]}")
        elif op_name == "REDUCE":
            logger.debug(f"Reducing {stack[-2]} with {stack[-1]}")
        elif op_name == "DUP":
            logger.debug(f"Duplicating {stack[-1]}")
        elif op_name == "EXT1" or op_name == "EXT2" or op_name == "EXT4":
            logger.debug(f"Loading extension {stack[-1]}")
        elif op_name == "STACK_GLOBAL":
            logger.debug(f"Loading class {stack[-1]} from {stack[-2]}")
        elif op_name == "NEWOBJ_EX":
            self.temp.append(stack[-3])
            self.temp.append(stack[-2])
            self.temp.append(stack[-1])
            logger.debug(f"Loading class {stack[-3]} with {stack[-2]} and {stack[-1]}")
        elif op_name == "NEWOBJ":
            self.temp.append(stack[-2])
            self.temp.append(stack[-1])
            logger.debug(f"Loading class {stack[-2]} with {stack[-1]}")
        elif op_name == "TUPLE3":
            self.temp.append(stack[-3])
            self.temp.append(stack[-2])
            self.temp.append(stack[-1])
            logger.debug(f"Loading tuple {self.temp}")
        elif op_name == "TUPLE2":
            self.temp.append(stack[-2])
            self.temp.append(stack[-1])
            logger.debug(f"Loading tuple {self.temp}")
        elif op_name == "TUPLE1":
            self.temp.append(stack[-1])
            logger.debug(f"Loading tuple {self.temp}")
        elif op_name == "BINPERSID":
            logger.debug(f"Loading persistent {stack[-1]}")

    def postcall(self, op_name, stack=None, metastack=None, memo=None, pos=0, *args, **kwargs):
        if stack is None:
            return

        if op_name == "GLOBAL":
            klass = stack[-1]
            if hasattr(op_name, "__name__"):
                logger.debug(f"Loaded class {klass.__name__}")
            else:
                logger.debug(f"Loaded class {klass}")
        elif op_name == "NEWOBJ_EX":
            logger.debug(f"Loaded class {self.temp[-3]} with {self.temp[-2]} and {self.temp[-1]} as {stack[-1]}")
            self.temp.clear()
        elif op_name == "NEWOBJ":
            logger.debug(f"Loaded class {self.temp[-2]} with {self.temp[-1]} as {stack[-1]}")
            self.temp.clear()
        elif op_name == "EMPTY_SET" or op_name == "EMPTY_DICT" or op_name == "EMPTY_LIST" or op_name == "EMPTY_TUPLE":
            logger.debug(f"Loaded empty {stack[-1].__class__.__name__} {stack[-1]}")
        elif op_name == "TUPLE3" or op_name == "TUPLE2" or op_name == "TUPLE1":
            logger.debug(f"Loaded tuple {stack[-1]}: {self.temp}")
            self.temp.clear()
        elif op_name == "PERSID" or op_name == "BINPERSID":
            logger.debug(f"Loaded persistent {stack[-1]}")
        elif op_name == "NONE":
            logger.debug("Loaded None")
        elif op_name == "NEWFALSE" or op_name == "NEWTRUE":
            logger.debug(f"Loaded bool {stack[-1]}")
        elif op_name == "INT" or op_name == "BININT" or op_name == "BININT1" or op_name == "BININT2":
            logger.debug(f"Loaded int {stack[-1]}")
        elif op_name == "LONG" or op_name == "LONG1" or op_name == "LONG4":
            logger.debug(f"Loaded long {stack[-1]}")
        elif op_name == "FLOAT" or op_name == "BINFLOAT":
            logger.debug(f"Loaded float {stack[-1]}")
        elif op_name == "STRING" or op_name == "BINSTRING" or op_name == "SHORT_BINSTRING" or\
            op_name == "UNICODE" or op_name == "BINUNICODE" or op_name == "BINUNICODE8":
            logger.debug(f"Loaded string {stack[-1]}")
        elif op_name == "BINBYTES" or op_name == "BINBYTES8" or op_name == "BYTEARRAY8" or op_name == "SHORT_BINBYTES":
            logger.debug(f"Loaded bytes {stack[-1]}")
        elif op_name == "NEXT_BUFFER":
            logger.debug(f"Loaded buffer {stack[-1]}")
        elif op_name == "READONLY_BUFFER":
            logger.debug(f"Made buffer {stack[-1]} readonly")
