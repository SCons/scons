#!/usr/bin/env python
# MIT License
#
# Copyright The SCons Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

"""
Benchmarks for testing various possible implementations
of the is_Dict(), is_List() and is_String() functions in
SCons/Util.py.
"""

import types
from collections import UserDict, UserList, UserString, deque
from collections.abc import Iterable, MappingView, MutableMapping, MutableSequence

DictType = dict
ListType = list
StringType = str


# The original implementations, pretty straightforward checks for the
# type of the object and whether it's an instance of the corresponding
# User* type.

def original_is_Dict(e):
    return isinstance(e, (dict, UserDict))

def original_is_List(e):
    return isinstance(e, (list, UserList))

def original_is_String(e):
    return isinstance(e, (str, UserString))


# New candidates that explicitly check for whether the object is an
# InstanceType before calling isinstance() on the corresponding User*
# type. Update: meaningless in Python 3, InstanceType was only for
# old-style classes, so these are just removed.
# XXX

# New candidates that try more generic names from collections:

def new_is_Dict(e):
    return isinstance(e, MutableMapping)

def new_is_List(e):
    return isinstance(e, MutableSequence)

def new_is_String(e):
    return isinstance(e, (str, UserString))

# Improved candidates that cache the type(e) result in a variable
# before doing any checks.

def cache_type_e_is_Dict(e):
    t = type(e)
    return t is dict or isinstance(e, UserDict)

def cache_type_e_is_List(e):
    t = type(e)
    return t is list or isinstance(e, (UserList, deque))

def cache_type_e_is_String(e):
    t = type(e)
    return t is str or isinstance(e, UserString)


# Improved candidates that cache the type(e) result in a variable
# before doing any checks, but using the global names for
# DictType, ListType and StringType.

def global_cache_type_e_is_Dict(e):
    t = type(e)
    return t is DictType or isinstance(e, UserDict)

def global_cache_type_e_is_List(e):
    t = type(e)
    return t is ListType or isinstance(e, (UserList, deque))

def global_cache_type_e_is_String(e):
    t = type(e)
    return t is StringType or isinstance(e, UserString)


# Alternative that uses a myType() function to map the User* objects
# to their corresponding underlying types.
# Again, since this used InstanceType, it's not useful for Python 3.


# These are the actual test entry points

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
    """new_is_String"""
    for i in IterationList:
        new_is_String(obj)

def Func05(obj):
    """new_is_List"""
    for i in IterationList:
        new_is_List(obj)

def Func06(obj):
    """new_is_Dict"""
    for i in IterationList:
        new_is_Dict(obj)

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
        "deque",
        (deque([]),),
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
