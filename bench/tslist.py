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
Benchmarks for the Executor.TSList class (SCons/Executor.py).

TSList is a lazily-materialized stand-in for a $SOURCES / $TARGETS NodeList.
It only subclasses collections.UserList so is_Sequence() recognizes it, and
it forwards each operation to a freshly-created NodeList by calling self.func().
In Python 3, UserList -> MutableSequence -> Sequence, and Sequence supplies an
index-based __iter__, so *iterating* an unmodified TSList calls func() once per
element (plus one probe for IndexError) instead of once for the whole list.
For $SOURCES, where func() rebuilds an O(n) NodeList, that turns a single
expansion into O(n^2) work.

This benchmarks the cumulative forms for a possible fix:

    * orig                        - as currently released
    * orig + __iter__             - delegates to iter(self.func())
    * orig + __iter__ + __bool__  - adds bool(self.func())
    * proxy                       - no longer inherit from UserList

self.func() is simulated with an honest O(n) rebuild of a UserList of proxies,
matching what Executor._get_sources()/_get_targets() do.

Run with:

    python bench.py tslist.py
"""

from collections import UserList


class NodeList(UserList):
    """Stand-in for SCons.Util.NodeList (a UserList with .data)."""

    def __str__(self):
        return ' '.join(map(str, self.data))


class Node:
    """Minimal stand-in for a build Node; has a (memoized) subst proxy."""

    __slots__ = ('name', '_proxy')

    def __init__(self, name):
        self.name = name

    def get_subst_proxy(self):
        try:
            return self._proxy
        except AttributeError:
            self._proxy = self
            return self


def make_getter(nodes):
    """Return a callable mimicking Executor._get_sources().

    Each call walks all the nodes and builds a fresh NodeList of their
    substitution proxies, which is O(n) work - this is the expensive bit
    that an index-by-index iteration ends up repeating n times.
    """

    def getter():
        return NodeList([n.get_subst_proxy() for n in nodes])

    return getter


class TSListOrig(UserList):
    """Original $TARGETS/$SOURCES expansion: no __iter__, no __bool__."""

    def __init__(self, func):
        self.func = func

    def __getattr__(self, attr):
        nl = self.func()
        return getattr(nl, attr)

    def __getitem__(self, i):
        nl = self.func()
        return nl[i]

    def __str__(self):
        nl = self.func()
        return str(nl)

    def __repr__(self):
        nl = self.func()
        return repr(nl)


class TSListWithIter(TSListOrig):
    """Original plus an explicit __iter__ delegating to the NodeList."""

    def __iter__(self):
        return iter(self.func())


class TSListWithIterBool(TSListWithIter):
    """Original plus __iter__ plus an explicit __bool__."""

    def __bool__(self):
        return bool(self.func())

class SequenceProxy():
    __slots__ = ()


class TSListProxy(UserList):
    """Using proxy base class with __iter__ and __bool__"""

    def __init__(self, func):
        self.func = func

    def __getattr__(self, attr):
        nl = self.func()
        return getattr(nl, attr)

    def __getitem__(self, i):
        nl = self.func()
        return nl[i]

    def __iter__(self):
        return iter(self.func())

    def __bool__(self):
        return bool(self.func())

    def __str__(self):
        nl = self.func()
        return str(nl)

    def __repr__(self):
        nl = self.func()
        return repr(nl)


class TSListGetters(UserList):
    """Using proxy base class with __iter__ and __bool__"""

    def __init__(self, func):
        self.func = func
        self._nodelist = None

    @property
    def nodelist(self):
        if self._nodelist is not None:
            return self._nodelist
        self._nodelist = self.func()
        return self._nodelist


    def __getattr__(self, attr):
        return getattr(self.nodelist, attr)

    def __getitem__(self, i):
        return self.nodelist[i]

    def __iter__(self):
        return iter(self.nodelist)

    def __bool__(self):
        return bool(self.nodelist)

    def __str__(self):
        return str(self.nodelist)

    def __repr__(self):
        return repr(self.nodelist)


def _wrapper(cls, nodes):
    return cls(make_getter(nodes))


def Func01(nodes):
    """TSListOrig                 : iterate"""
    ts = _wrapper(TSListOrig, nodes)
    for i in IterationList:
        for x in ts:
            pass


def Func02(nodes):
    """TSListWithIter             : iterate"""
    ts = _wrapper(TSListWithIter, nodes)
    for i in IterationList:
        for x in ts:
            pass


def Func03(nodes):
    """TSListWithIterBool         : iterate"""
    ts = _wrapper(TSListWithIterBool, nodes)
    for i in IterationList:
        for x in ts:
            pass


def Func04(nodes):
    """TSListProxy                : iterate"""
    ts = _wrapper(TSListProxy, nodes)
    for i in IterationList:
        for x in ts:
            pass


def Func04a(nodes):
    """TSListGetters              : iterate"""
    ts = _wrapper(TSListGetters, nodes)
    for i in IterationList:
        for x in ts:
            pass


def Func05(nodes):
    """TSListOrig                 : if ts"""
    ts = _wrapper(TSListOrig, nodes)
    for i in IterationList:
        if ts:
            pass


def Func06(nodes):
    """TSListWithIter             : if ts"""
    ts = _wrapper(TSListWithIter, nodes)
    for i in IterationList:
        if ts:
            pass


def Func07(nodes):
    """TSListWithIterBool         : if ts"""
    ts = _wrapper(TSListWithIterBool, nodes)
    for i in IterationList:
        if ts:
            pass


def Func08(nodes):
    """TSListProxy                : if ts"""
    ts = _wrapper(TSListProxy, nodes)
    for i in IterationList:
        if ts:
            pass


def Func09(nodes):
    """TSListOrig                 : list(ts)"""
    ts = _wrapper(TSListOrig, nodes)
    for i in IterationList:
        list(ts)


def Func10(nodes):
    """TSListWithIter             : list(ts)"""
    ts = _wrapper(TSListWithIter, nodes)
    for i in IterationList:
        list(ts)


def Func11(nodes):
    """TSListWithIterBool         : list(ts)"""
    ts = _wrapper(TSListWithIterBool, nodes)
    for i in IterationList:
        list(ts)


def Func12(nodes):
    """TSListProxy                : list(ts)"""
    ts = _wrapper(TSListProxy, nodes)
    for i in IterationList:
        list(ts)


# Data to pass to the functions on each run.  Each entry is a
# three-element tuple:
#
#   (
#       "Label to print describing this data run",
#       ('positional', 'arguments'),
#       {'keyword' : 'arguments'},
#   ),

# Nested lists of source-like Nodes.  Orig iteration is O(n^2) in the
# number of nodes, so keep the sizes modest; bump them (or run with fewer
# -i iterations) to push the quadratic curve further.

def _nodes(n):
    return [Node(f'source{i:04d}') for i in range(n)]


Data = [
    (
        "16 nodes",
        (_nodes(16),),
        {},
    ),
    (
        "64 nodes",
        (_nodes(64),),
        {},
    ),
    (
        "256 nodes",
        (_nodes(256),),
        {},
    ),
]
