import pickle
import os
import fastapi
import ast


pickle_data = pickle.dumps(EvilPickle())
with open("pickle.pkl", "wb") as file:
    file.write(pickle_data)

# with open("myclass.pkl", "wb") as f:
#     pickle.dump("test", f)
