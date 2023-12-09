import pickle

OPCODES = pickle._Unpickler.dispatch.keys()

OPCODE_NAME_MAPPING = {}    # A bytes (with only one byte) to opcode name string mapping
pickle_objects_dict = pickle.__dict__
for k in pickle_objects_dict:
    pickle_object = pickle_objects_dict[k]
    if isinstance(pickle_object, bytes) and len(pickle_object) == 1:
        if int(pickle_object[0]) in OPCODES:
            OPCODE_NAME_MAPPING[pickle_object] = k
