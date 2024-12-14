import pickle

# Import parent directory
import sys
sys.path.append("..")

if __name__ == "__main__":
    # Dump an integer
    with open("int1_v3.pkl", "wb") as f:
        pickle.dump(255, f, protocol=3)
    with open("int2_v3.pkl", "wb") as f:
        pickle.dump(65535, f, protocol=3)
    with open("int_v3.pkl", "wb") as f:
        pickle.dump(-256, f, protocol=3)

    with open("long.pkl", "wb") as f:
        pickle.dump(2**64, f, protocol=1)
    # Dump a long less than 256 bytes
    with open("long1.pkl", "wb") as f:
        pickle.dump(2**(254 * 8), f, protocol=3)
    with open("long4.pkl", "wb") as f:
        pickle.dump(2**(255 * 8), f, protocol=3)

    with open("true.pkl", "wb") as f:
        pickle.dump(True, f, protocol=3)
    with open("false.pkl", "wb") as f:
        pickle.dump(False, f, protocol=3)

    with open("none.pkl", "wb") as f:
        pickle.dump(None, f, protocol=3)

    with open("float.pkl", "wb") as f:
        pickle.dump(0.3, f, protocol=3)

    with open("str.pkl", "wb") as f:
        pickle.dump("hello", f)
    with open("str_v3.pkl", "wb") as f:
        pickle.dump("hello", f, protocol=3)

    with open("list.pkl", "wb") as f:
        pickle.dump([1, 2, 3], f)
    with open("list_v3.pkl", "wb") as f:
        pickle.dump([1, 2, 3], f, protocol=3)

    with open("dict.pkl", "wb") as f:
        pickle.dump({"a": 1, "b": 2}, f)
    with open("dict_v3.pkl", "wb") as f:
        pickle.dump({"a": 1, "b": 2}, f, protocol=3)

    with open("tuple.pkl", "wb") as f:
        pickle.dump((1, 2, 3), f)
    with open("tuple_v3.pkl", "wb") as f:
        pickle.dump((1, 2, 3), f, protocol=3)
    with open("tuple_more_elements.pkl", "wb") as f:
        pickle.dump((1, 2, 3, 4), f)
    with open("tuple_more_elements_v3.pkl", "wb") as f:
        pickle.dump((1, 2, 3, 4), f, protocol=3)

    with open("set.pkl", "wb") as f:
        # Protocol 4 imports empty set, which does not require global import
        pickle.dump({1, 2, 3}, f)
    with open("set_v3.pkl", "wb") as f:
        pickle.dump({1, 2, 3}, f, protocol=3)

    # Protocol 4 only
    if pickle.HIGHEST_PROTOCOL >= 4:
        with open("frozenset.pkl", "wb") as f:
            pickle.dump(frozenset({1, 2, 3}), f)

    with open("bytes.pkl", "wb") as f:
        pickle.dump(b"hello", f)
    with open("bytes_v2.pkl", "wb") as f:
        pickle.dump(b"hello", f, protocol=2)
    with open("bytes_v3.pkl", "wb") as f:
        pickle.dump(b"hello", f, protocol=3)

    with open("bytearray.pkl", "wb") as f:
        pickle.dump(bytearray(b"hello"), f)
    with open("bytearray_v3.pkl", "wb") as f:
        pickle.dump(bytearray(b"hello"), f, protocol=3)

    with open("global.pkl", "wb") as f:
        # Stack global
        from pickletools import dis
        pickle.dump(dis, f)
    with open("global_v3.pkl", "wb") as f:
        # Old global
        from pickletools import dis
        pickle.dump(dis, f, protocol=3)

    with open("class_v3.pkl", "wb") as f:
        from examples.myclass import MyClass
        pickle.dump(MyClass(False), f, protocol=3)
