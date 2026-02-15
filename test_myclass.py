from myclass import MyClass
import pickle

with open("class.pkl", "wb") as f:
    pickle.dump(MyClass(False), f, protocol=3)
