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
        self.state = None
        self.parents = []
        
        for kid in kids:
            kid.parents.append(self)
            
    def build(self):
        global built
        built = self.name + " built"

    def children(self):
	return self.kids

    def get_parents(self):
        return self.parents
    
    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state

    def children_are_executed(self):
        return reduce(lambda x,y: ((y.get_state() == SCons.Node.executed
                                   or y.get_state() == SCons.Node.up_to_date)
                                   and x),
                      self.children(),
                      1)
    


class TaskmasterTestCase(unittest.TestCase):

    def test_next_task(self):
	"""Test fetching the next task
	"""
	global built

        n1 = Node("n1")
        tm = SCons.Taskmaster.Taskmaster([n1,n1])
        t = tm.next_task()
        tm.executed(t)
        t = tm.next_task()
        assert t == None

        
	n1 = Node("n1")
	n2 = Node("n2")
        n3 = Node("n3", [n1, n2])
        
	tm = SCons.Taskmaster.Taskmaster([n3])

        t = tm.next_task()
        t.execute()
        assert built == "n1 built"
        tm.executed(t)

        t = tm.next_task()
        t.execute()
        assert built == "n2 built"
        tm.executed(t)

        t = tm.next_task()
        t.execute()
        assert built == "n3 built"
        tm.executed(t)

        assert tm.next_task() == None

	def current(node):
	    return 1

	built = "up to date: "

        global top_node
        top_node = n3
	class MyTM(SCons.Taskmaster.Taskmaster):
	    def up_to_date(self, node, top):
                if node == top_node:
                    assert top
                global built
                built = built + " " + node.name


        n1.set_state(None)
        n2.set_state(None)
        n3.set_state(None)
	tm = MyTM(targets = [n3], current = current)
	assert tm.next_task() == None
        print built
	assert built == "up to date:  n1 n2 n3"


        n1 = Node("n1")
	n2 = Node("n2")
        n3 = Node("n3", [n1, n2])
        n4 = Node("n4")
        n5 = Node("n5", [n3, n4])
        tm = SCons.Taskmaster.Taskmaster([n5])

        assert not tm.is_blocked()
        
        t1 = tm.next_task()
        assert t1.get_target() == n1
        assert not tm.is_blocked()
        
        t2 = tm.next_task()
        assert t2.get_target() == n2
        assert not tm.is_blocked()

        t4 = tm.next_task()
        assert t4.get_target() == n4
        assert tm.is_blocked()
        tm.executed(t4)
        assert tm.is_blocked()
        
        tm.executed(t1)
        assert tm.is_blocked()
        tm.executed(t2)
        assert not tm.is_blocked()
        t3 = tm.next_task()
        assert t3.get_target() == n3
        assert tm.is_blocked()

        tm.executed(t3)
        assert not tm.is_blocked()
        t5 = tm.next_task()
        assert t5.get_target() == n5
        assert not tm.is_blocked()

        assert tm.next_task() == None

        
        n4 = Node("n4")
        n4.set_state(SCons.Node.executed)
        tm = SCons.Taskmaster.Taskmaster([n4])
        assert tm.next_task() == None

    def test_is_blocked(self):
        """Test whether a task is blocked

	Both default and overridden in a subclass.
	"""
	tm = SCons.Taskmaster.Taskmaster()
	assert not tm.is_blocked()

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
        foo = Node('foo')
	tm.executed(SCons.Taskmaster.Task(foo))

	class MyTM(SCons.Taskmaster.Taskmaster):
	    def executed(self, task):
	        return 'x' + task
	tm = MyTM()
	assert tm.executed('foo') == 'xfoo'

    def test_ignore_errors(self):
        n1 = Node("n1")
        n2 = Node("n2")
        n3 = Node("n3", [n1])
        
        tm = SCons.Taskmaster.Taskmaster([n3, n2],
                                         SCons.Taskmaster.Task,
                                         SCons.Taskmaster.current,
                                         1)

        t = tm.next_task()
        assert t.get_target() == n1
        tm.failed(t)
        t = tm.next_task()
        assert t.get_target() == n3
        tm.failed(t)
        t = tm.next_task()
        assert t.get_target() == n2
        

    def test_keep_going(self):
        n1 = Node("n1")
        n2 = Node("n2")
        n3 = Node("n3", [n1])
        
        tm = SCons.Taskmaster.Taskmaster([n3, n2],
                                         SCons.Taskmaster.Task,
                                         SCons.Taskmaster.current,
                                         0,
                                         1)

        tm.failed(tm.next_task())
        t = tm.next_task()
        assert t.get_target() == n2
        tm.executed(t)
        assert not tm.is_blocked()
        t = tm.next_task()
        assert t == None


    def test_failed(self):
        """Test the failed() method

	Both default and overridden in a subclass.
	"""
        foo = Node('foo')
        bar = Node('bar')
        tm = SCons.Taskmaster.Taskmaster([foo,bar])
        tm.failed(tm.next_task())
        assert tm.next_task() == None
        
	class MyTM(SCons.Taskmaster.Taskmaster):
	    def failed(self, task):
	        return 'y' + task
	tm = MyTM()
	assert tm.failed('foo') == 'yfoo'




if __name__ == "__main__":
    suite = unittest.makeSuite(TaskmasterTestCase, 'test_')
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
	sys.exit(1)
