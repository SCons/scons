# __COPYRIGHT__
#
# Benchmarks for testing various possible implementations
# of the is_Dict(), is_List() and is_String() functions in
# src/engine/SCons/Util.py.

import types
from UserDict import UserDict
from UserList import UserList

try:
    from UserString import UserString
except ImportError:
    # "Borrowed" from the Python 2.2 UserString module
    # and modified slightly for use with SCons.
    class UserString:
        def __init__(self, seq):
            if type(seq) == type(''):
                self.data = seq
            elif isinstance(seq, UserString):
                self.data = seq.data[:]
            else:
                self.data = str(seq)
        def __str__(self): return str(self.data)
        def __repr__(self): return repr(self.data)
        def __int__(self): return int(self.data)
        def __long__(self): return long(self.data)
        def __float__(self): return float(self.data)
        def __complex__(self): return complex(self.data)
        def __hash__(self): return hash(self.data)

        def __cmp__(self, string):
            if isinstance(string, UserString):
                return cmp(self.data, string.data)
            else:
                return cmp(self.data, string)
        def __contains__(self, char):
            return char in self.data

        def __len__(self): return len(self.data)
        def __getitem__(self, index): return self.__class__(self.data[index])
        def __getslice__(self, start, end):
            start = max(start, 0); end = max(end, 0)
            return self.__class__(self.data[start:end])

        def __add__(self, other):
            if isinstance(other, UserString):
                return self.__class__(self.data + other.data)
            elif is_String(other):
                return self.__class__(self.data + other)
            else:
                return self.__class__(self.data + str(other))
        def __radd__(self, other):
            if is_String(other):
                return self.__class__(other + self.data)
            else:
                return self.__class__(str(other) + self.data)
        def __mul__(self, n):
            return self.__class__(self.data*n)
        __rmul__ = __mul__

InstanceType = types.InstanceType
DictType = types.DictType
ListType = types.ListType
StringType = types.StringType
if hasattr(types, 'UnicodeType'):
    UnicodeType = types.UnicodeType


# The original implementations, pretty straightforward checks for the
# type of the object and whether it's an instance of the corresponding
# User* type.

def original_is_Dict(e):
    return type(e) is types.DictType or isinstance(e, UserDict)

def original_is_List(e):
    return type(e) is types.ListType or isinstance(e, UserList)

if hasattr(types, 'UnicodeType'):
    def original_is_String(e):
        return type(e) is types.StringType \
            or type(e) is types.UnicodeType \
            or isinstance(e, UserString)
else:
    def original_is_String(e):
        return type(e) is types.StringType or isinstance(e, UserString)



# New candidates that explicitly check for whether the object is an
# InstanceType before calling isinstance() on the corresponding User*
# type.

def checkInstanceType_is_Dict(e):
    return type(e) is types.DictType or \
           (type(e) is types.InstanceType and isinstance(e, UserDict))

def checkInstanceType_is_List(e):
    return type(e) is types.ListType \
        or (type(e) is types.InstanceType and isinstance(e, UserList))

if hasattr(types, 'UnicodeType'):
    def checkInstanceType_is_String(e):
        return type(e) is types.StringType \
            or type(e) is types.UnicodeType \
            or (type(e) is types.InstanceType and isinstance(e, UserString))
else:
    def checkInstanceType_is_String(e):
        return type(e) is types.StringType \
            or (type(e) is types.InstanceType and isinstance(e, UserString))



# Improved candidates that cache the type(e) result in a variable
# before doing any checks.

def cache_type_e_is_Dict(e):
    t = type(e)
    return t is types.DictType or \
           (t is types.InstanceType and isinstance(e, UserDict))

def cache_type_e_is_List(e):
    t = type(e)
    return t is types.ListType \
        or (t is types.InstanceType and isinstance(e, UserList))

if hasattr(types, 'UnicodeType'):
    def cache_type_e_is_String(e):
        t = type(e)
        return t is types.StringType \
            or t is types.UnicodeType \
            or (t is types.InstanceType and isinstance(e, UserString))
else:
    def cache_type_e_is_String(e):
        t = type(e)
        return t is types.StringType \
            or (t is types.InstanceType and isinstance(e, UserString))



# Improved candidates that cache the type(e) result in a variable
# before doing any checks, but using the global names for
# DictType, ListType and StringType.

def global_cache_type_e_is_Dict(e):
    t = type(e)
    return t is DictType or \
           (t is InstanceType and isinstance(e, UserDict))

def global_cache_type_e_is_List(e):
    t = type(e)
    return t is ListType \
        or (t is InstanceType and isinstance(e, UserList))

if hasattr(types, 'UnicodeType'):
    def global_cache_type_e_is_String(e):
        t = type(e)
        return t is StringType \
            or t is UnicodeType \
            or (t is InstanceType and isinstance(e, UserString))
else:
    def global_cache_type_e_is_String(e):
        t = type(e)
        return t is StringType \
            or (t is InstanceType and isinstance(e, UserString))



# Alternative that uses a myType() function to map the User* objects
# to their corresponding underlying types.

instanceTypeMap = {
    UserDict : types.DictType,
    UserList : types.ListType,
    UserString : types.StringType,
}

if hasattr(types, 'UnicodeType'):
    def myType(obj):
        t = type(obj)
        if t is types.InstanceType:
            t = instanceTypeMap.get(obj.__class__, t)
        elif t is types.UnicodeType:
            t = types.StringType
        return t
else:
    def myType(obj):
        t = type(obj)
        if t is types.InstanceType:
            t = instanceTypeMap.get(obj.__class__, t)
        return t

def myType_is_Dict(e):
    return myType(e) is types.DictType

def myType_is_List(e):
    return myType(e) is types.ListType

def myType_is_String(e):
    return myType(e) is types.StringType




def Func01(obj):
    """original_is_String"""
    for i in IterationList:
        original_is_String(obj)

def Func02(obj):
    """original_is_List"""
    for i in IterationList:
        original_is_List(obj)

def Func03(obj):
    """original_is_Dict"""
    for i in IterationList:
        original_is_Dict(obj)

def Func04(obj):
    """checkInstanceType_is_String"""
    for i in IterationList:
        checkInstanceType_is_String(obj)

def Func05(obj):
    """checkInstanceType_is_List"""
    for i in IterationList:
        checkInstanceType_is_List(obj)

def Func06(obj):
    """checkInstanceType_is_Dict"""
    for i in IterationList:
        checkInstanceType_is_Dict(obj)

def Func07(obj):
    """cache_type_e_is_String"""
    for i in IterationList:
        cache_type_e_is_String(obj)

def Func08(obj):
    """cache_type_e_is_List"""
    for i in IterationList:
        cache_type_e_is_List(obj)

def Func09(obj):
    """cache_type_e_is_Dict"""
    for i in IterationList:
        cache_type_e_is_Dict(obj)

def Func10(obj):
    """global_cache_type_e_is_String"""
    for i in IterationList:
        global_cache_type_e_is_String(obj)

def Func11(obj):
    """global_cache_type_e_is_List"""
    for i in IterationList:
        global_cache_type_e_is_List(obj)

def Func12(obj):
    """global_cache_type_e_is_Dict"""
    for i in IterationList:
        global_cache_type_e_is_Dict(obj)

#def Func13(obj):
#    """myType_is_String"""
#    for i in IterationList:
#        myType_is_String(obj)
#
#def Func14(obj):
#    """myType_is_List"""
#    for i in IterationList:
#        myType_is_List(obj)
#
#def Func15(obj):
#    """myType_is_Dict"""
#    for i in IterationList:
#        myType_is_Dict(obj)



# Data to pass to the functions on each run.  Each entry is a
# three-element tuple:
#
#   (
#       "Label to print describing this data run",
#       ('positional', 'arguments'),
#       {'keyword' : 'arguments'},
#   ),

class A:
    pass

Data = [
    (
        "String",
        ('',),
        {},
    ),
    (
        "List",
        ([],),
        {},
    ),
    (
        "Dict",
        ({},),
        {},
    ),
    (
        "UserString",
        (UserString(''),),
        {},
    ),
    (
        "UserList",
        (UserList([]),),
        {},
    ),
    (
        "UserDict",
        (UserDict({}),),
        {},
    ),
    (
        "Object",
        (A(),),
        {},
    ),
]

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
