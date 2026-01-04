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
#

"""
Benchmarks for testing the selection of dependency changed functions
in src/engine/Environment.py.
"""


def use_a_dict(env, dep, arg):
    func = {
        '1111' : dep.func1,
        '2222' : dep.func2,
        '3333' : dep.func3,
        '4444' : dep.func4,
    }
    t = env.get_type()
    return func[t](arg)


def use_if_tests(env, dep, arg):
    t = env.get_type()
    if t == '1111':
        func = dep.func1
    elif t == '2222':
        func = dep.func2
    elif t == '3333':
        func = dep.func3
    elif t == '4444':
        func = dep.func4
    else:
        raise Exception("bad key %s" % t)
    return func(arg)


class Environment():
    def __init__(self, t):
        self.t = t
    def get_type(self):
        return self.t

class Node():
    def func1(self, arg):
        pass
    def func2(self, arg):
        pass
    def func3(self, arg):
        pass
    def func4(self, arg):
        pass

node = Node()

def Func01(t):
    """use_a_dict"""
    env = Environment(t)
    for i in IterationList:
        use_a_dict(env, node, None)

def Func02(t):
    """use_if_tests"""
    env = Environment(t)
    for i in IterationList:
        use_if_tests(env, node, None)



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
        "1",
        ('1111',),
        {},
    ),
    (
        "2",
        ('2222',),
        {},
    ),
    (
        "3",
        ('3333',),
        {},
    ),
    (
        "4",
        ('4444',),
        {},
    ),
]
