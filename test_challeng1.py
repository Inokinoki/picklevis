from challenge1 import MyFunction, challenge1
import pickle
import cloudpickle

def challenge2(name, description, value="test", *args, **kwargs):
    print(name, description, value, args, kwargs)

if __name__ == "__main__":
    with open("challenge1.pkl", "wb") as f:
        pickle.dump(challenge1, f, protocol=3)
    with open("challenge1_cloud_py39.pkl", "wb") as f:
        cloudpickle.dump(challenge2, f, protocol=3)

