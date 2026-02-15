import types

def reduce_function(code, name):
    return types.FunctionType(code, {}, name, None, None)

def reduce_code(obj):
    co_name = "".join(obj.co_name)
    co_names = tuple(name for name in obj.co_names)
    co_varnames = tuple(name for name in obj.co_varnames)
    co_freevars = tuple(name for name in obj.co_freevars)
    co_cellvars = tuple(name for name in obj.co_cellvars)
    return types.CodeType, (
        obj.co_argcount,
        obj.co_posonlyargcount,
        obj.co_kwonlyargcount,
        obj.co_nlocals,
        obj.co_stacksize,
        obj.co_flags,
        obj.co_code,
        obj.co_consts,
        co_names,
        co_varnames,
        obj.co_filename,
        co_name,
        obj.co_firstlineno,
        obj.co_linetable,
        co_freevars,
        co_cellvars,
    )
