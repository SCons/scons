__revision__ = "Node/NodeTests.py __REVISION__ __DATE__ __DEVELOPER__"

import os
import sys
import unittest

import SCons.Node



built_it = None

class Builder:
    def execute(self, target = None, source = None):
	global built_it
	built_it = 1



class NodeTestCase(unittest.TestCase):

    def test_build(self):
	"""Test building a node
	"""
	node = SCons.Node.Node()
	node.builder_set(Builder())
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



if __name__ == "__main__":
    suite = unittest.makeSuite(NodeTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
