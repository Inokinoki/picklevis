
class MyFunction:
    def __init__(self, func):
        self.func = func


def challenge1(name, description, value="test", *args, **kwargs):
    print(name, description, value, args, kwargs)

