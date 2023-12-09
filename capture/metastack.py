import logging

from capture.base import PicklevisCapturer


logger = logging.getLogger(__file__)


class MetastackCapture(PicklevisCapturer):
    def __init__(self) -> None:
        super().__init__()

    def precall(self, op_name, stack=None, metastack=None, memo=None, pos=0, *args, **kwargs):
        if metastack is not None:
            if op_name == "APPENDS":
                logger.debug(f"Appending {len(metastack[-1])} items to list")
            elif op_name == "SETITEMS":
                logger.debug(f"Setting {len(metastack[-1])} items to dict")
            elif op_name == "ADDITEMS":
                logger.debug(f"Adding {len(metastack[-1])} items to dict")

            elif op_name == "LIST":
                logger.debug(f"Creating a list with {len(metastack[-1])} items")
            elif op_name == "INST":
                logger.debug(f"Creating an instance with {len(metastack[-1])} items")
            elif op_name == "DICT":
                logger.debug(f"Creating a dict with {len(metastack[-1])} items")
            elif op_name == "OBJ":
                logger.debug(f"Creating an object with {len(metastack[-1])} items")
            elif op_name == "FROZENSET":
                logger.debug(f"Creating a frozen set with {len(metastack[-1])} items")
            elif op_name == "TUPLE":
                logger.debug(f"Creating a tuple with {len(metastack[-1])} items")

            elif op_name == "POP_MARK" or op_name == "POP" and stack is None:
                logger.debug("Dropping a meta stack")


    def postcall(self, op_name, stack=None, metastack=None, memo=None, pos=0, *args, **kwargs):
        if op_name == "MARK" and metastack is not None:
            logger.debug("Pushed the current stack to metastack")
