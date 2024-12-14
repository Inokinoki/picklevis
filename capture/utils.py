import copy

def copy_without_object(obj):
    # For all objects that are not from python's built-in types, we will copy them
    # to avoid modifying the original object.
    if isinstance(obj, (list, tuple, dict, set)):
        return copy.copy(obj)
    else:
        return obj

def copy_stack(stack):
    return [copy_without_object(e) for e in stack]
