import pickle

if __name__ == "__main__":
    # Dump an integer
    with open("int1.pkl", "wb") as f:
        pickle.dump(0, f)

    with open("bool.pkl", "wb") as f:
        pickle.dump(True, f)

    with open("float.pkl", "wb") as f:
        pickle.dump(0.3, f)

    with open("str.pkl", "wb") as f:
        pickle.dump("hello", f)

    with open("list.pkl", "wb") as f:
        pickle.dump([1, 2, 3], f)

    with open("dict.pkl", "wb") as f:
        pickle.dump({"a": 1, "b": 2}, f)

    with open("tuple.pkl", "wb") as f:
        pickle.dump((1, 2, 3), f)

    with open("set.pkl", "wb") as f:
        pickle.dump({1, 2, 3}, f)

    # Protocol 4
    with open("frozenset.pkl", "wb") as f:
        pickle.dump(frozenset({1, 2, 3}), f)

    with open("bytes.pkl", "wb") as f:
        pickle.dump(b"hello", f)

    with open("bytearray.pkl", "wb") as f:
        pickle.dump(bytearray(b"hello"), f)

    with open("none.pkl", "wb") as f:
        pickle.dump(None, f)
