import pickle
import types

from test_challenge1_helper import reduce_code, reduce_function

_BUILTIN_TYPE_NAMES = {}
for k, v in types.__dict__.items():
    if type(v) is type:
        _BUILTIN_TYPE_NAMES[v] = k






class MyFunctionPickler(pickle.Pickler):
    def __init__(self, *args, **kwargs):
        super(MyFunctionPickler, self).__init__(*args, **kwargs)
        self.functions_should_pickle = []
        self.whilelist_code = []

    def reducer_override(self, obj):
        print(obj.__class__)
        if isinstance(obj, types.FunctionType) and obj.__name__ in self.functions_should_pickle:
            print(obj.__name__)
            self.whilelist_code.append(obj.__code__)
            return reduce_function, (obj.__code__, obj.__name__)
        if isinstance(obj, types.CodeType) and obj in self.whilelist_code:
            return reduce_code(obj)
        return NotImplemented


def challenge1(name, description, value="test", *args, **kwargs):
    print(name, description, value, args, kwargs)

if __name__ == "__main__":
    with open("challenge1.pkl", "wb") as f:
        pickler = MyFunctionPickler(f, protocol=3)
        pickler.functions_should_pickle = [challenge1.__name__]
        pickler.dump(challenge1)
