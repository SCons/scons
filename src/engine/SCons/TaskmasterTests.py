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

import sys
import unittest

import SCons.Taskmaster



built = None

class Node:
    def __init__(self, name, kids = []):
        self.name = name
	self.kids = kids

    def build(self):
        global built
        built = self.name + " built"

    def children(self):
	return self.kids



class TaskmasterTestCase(unittest.TestCase):

    def test_next_node(self):
	"""Test fetching the next node
	"""
	n1 = Node("n1")
	n2 = Node("n2")
	n3 = Node("n3", [n1, n2])

	tm = SCons.Taskmaster.Taskmaster([n3])
	n, top = tm.next_node()
	assert n.name == "n1"
	assert top == None
	n, top = tm.next_node()
	assert n.name == "n2"
	assert top == None
	n, top = tm.next_node()
	assert n.name == "n3"
	assert top == 1
	n, top = tm.next_node()
	assert n == None
	assert top == None

    def test_next_task(self):
	"""Test fetching the next task
	"""
	global built

	n1 = Node("n1")
	n2 = Node("n2")
	n3 = Node("n3", [n1, n2])

	tm = SCons.Taskmaster.Taskmaster([n3])
	tm.next_task().execute()
	assert built == "n1 built"

	tm.next_task().execute()
	assert built == "n2 built"

	tm.next_task().execute()
	assert built == "n3 built"

	def current(node):
	    return 1

	built = "up to date: "

	class MyTM(SCons.Taskmaster.Taskmaster):
	    def up_to_date(self, node):
		global built
	        built = built + " " + node.name

	tm = MyTM(targets = [n3], current = current)
	assert tm.next_task() == None
	assert built == "up to date:  n1 n2 n3"

    def test_is_blocked(self):
        """Test whether a task is blocked

	Both default and overridden in a subclass.
	"""
	tm = SCons.Taskmaster.Taskmaster()
	assert tm.is_blocked() == 0

	class MyTM(SCons.Taskmaster.Taskmaster):
	    def is_blocked(self):
	        return 1
	tm = MyTM()
	assert tm.is_blocked() == 1

    def test_executed(self):
        """Test the executed() method

	Both default and overridden in a subclass.
	"""
	tm = SCons.Taskmaster.Taskmaster()
	tm.executed('foo')

	class MyTM(SCons.Taskmaster.Taskmaster):
	    def executed(self, task):
	        return 'x' + task
	tm = MyTM()
	assert tm.executed('foo') == 'xfoo'

    def test_failed(self):
        """Test the failed() method

	Both default and overridden in a subclass.
	"""
	tm = SCons.Taskmaster.Taskmaster()
	#XXX
	tm.failed('foo')

	class MyTM(SCons.Taskmaster.Taskmaster):
	    def failed(self, task):
	        return 'y' + task
	tm = MyTM()
	assert tm.failed('foo') == 'yfoo'




if __name__ == "__main__":
    suite = unittest.makeSuite(TaskmasterTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
