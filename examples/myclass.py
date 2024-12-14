
class MyClass:
    def __init__(self, value, avalue=0):
        self.value = value
        self.avalue = avalue

    def __getstate__(self):
        return {
            "value": self.value,
            "avalue": self.avalue,
        }

    def __setstate__(self, state):
        self.value = state["value"]
        self.avalue = state["avalue"]
