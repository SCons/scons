#
# Copyright (c) 2001 Steven Knight
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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import sys
import unittest

import SCons.Errors
import SCons.Node



built_it = None

class Builder:
    def execute(self, **kw):
	global built_it
	built_it = 1
        return 0

class FailBuilder:
    def execute(self, **kw):
        return 1

class Environment:
    def Dictionary(self, *args):
	pass



class NodeTestCase(unittest.TestCase):

    def test_BuildException(self):
	"""Test throwing an exception on build failure.
	"""
	node = SCons.Node.Node()
	node.builder_set(FailBuilder())
	node.env_set(Environment())
	try:
	    node.build()
	except SCons.Errors.BuildError:
	    pass
	else:
	    raise TestFailed, "did not catch expected BuildError"

    def test_build(self):
	"""Test building a node
	"""
	node = SCons.Node.Node()
	node.builder_set(Builder())
	node.env_set(Environment())
	node.path = "xxx"	# XXX FAKE SUBCLASS ATTRIBUTE
	node.sources = "yyy"	# XXX FAKE SUBCLASS ATTRIBUTE
	node.build()
	assert built_it

    def test_builder_set(self):
	"""Test setting a Node's Builder
	"""
	node = SCons.Node.Node()
	b = Builder()
	node.builder_set(b)
	assert node.builder == b

    def test_env_set(self):
	"""Test setting a Node's Environment
	"""
	node = SCons.Node.Node()
	e = Environment()
	node.env_set(e)
	assert node.env == e

    def test_has_signature(self):
	"""Test whether or not a node has a signature
	"""
	node = SCons.Node.Node()
	assert not node.has_signature()
	node.set_signature('xxx')
	assert node.has_signature()

    def test_set_signature(self):
	"""Test setting a Node's signature
	"""
	node = SCons.Node.Node()
	node.set_signature('yyy')
        assert node.signature == 'yyy'

    def test_get_signature(self):
	"""Test fetching a Node's signature
	"""
	node = SCons.Node.Node()
	node.set_signature('zzz')
        assert node.get_signature() == 'zzz'

    def test_add_dependency(self):
	"""Test adding dependencies to a Node's list.
	"""
	node = SCons.Node.Node()
	assert node.depends == []
	try:
	    node.add_dependency('zero')
	except TypeError:
	    pass
	node.add_dependency(['one'])
	assert node.depends == ['one']
	node.add_dependency(['two', 'three'])
	assert node.depends == ['one', 'two', 'three']

    def test_add_source(self):
	"""Test adding sources to a Node's list.
	"""
	node = SCons.Node.Node()
	assert node.sources == []
	try:
	    node.add_source('zero')
	except TypeError:
	    pass
	node.add_source(['one'])
	assert node.sources == ['one']
	node.add_source(['two', 'three'])
	assert node.sources == ['one', 'two', 'three']

    def test_children(self):
	"""Test fetching the "children" of a Node.
	"""
	node = SCons.Node.Node()
	node.add_source(['one', 'two', 'three'])
	node.add_dependency(['four', 'five', 'six'])
	kids = node.children()
	kids.sort()
	print kids
	assert kids == ['five', 'four', 'one', 'six', 'three', 'two']



if __name__ == "__main__":
    suite = unittest.makeSuite(NodeTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
