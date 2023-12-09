

class PicklevisCapturer:
    def __init__(self) -> None:
        pass

    def precall(self, op_name, stack=None, metastack=None, memo=None, pos=0, *args, **kwargs):
        ...

    def postcall(self, op_name, stack=None, metastack=None, memo=None, pos=0, *args, **kwargs):
        ...
