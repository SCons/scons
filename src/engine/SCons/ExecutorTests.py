#
# __COPYRIGHT__
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

import string
import sys
import unittest

import SCons.Executor


class MyEnvironment:
    def __init__(self, **kw):
        self._dict = {}
        self._dict.update(kw)
    def Override(self, overrides):
        d = self._dict.copy()
        d.update(overrides)
        return d

class MyAction:
    actions = ['action1', 'action2']
    def get_actions(self):
        return self.actions
    def get_raw_contents(self, target, source, env):
        return string.join(['RAW'] + self.actions + target + source)
    def get_contents(self, target, source, env):
        return string.join(self.actions + target + source)

class MyBuilder:
    def __init__(self, env, overrides):
        self.env = env
        self.overrides = overrides
        self.action = MyAction()

class MyNode:
    def __init__(self, pre, post):
        self.pre_actions = pre
        self.post_actions = post
        

class ExecutorTestCase(unittest.TestCase):

    def test__init__(self):
        """Test creating an Executor"""
        source_list = ['s1', 's2']
        x = SCons.Executor.Executor('b', 'e', 'o', 't', source_list)
        assert x.builder == 'b', x.builder
        assert x.env == 'e', x.env
        assert x.overrides == 'o', x.overrides
        assert x.targets == 't', x.targets
        source_list.append('s3')
        assert x.sources == ['s1', 's2'], x.sources

    def test_get_build_env(self):
        """Test fetching and generating a build environment"""
        x = SCons.Executor.Executor('b', 'e', 'o', 't', ['s1', 's2'])
        x.build_env = 'eee'
        be = x.get_build_env()
        assert be == 'eee', be

        x = SCons.Executor.Executor('b',
                                    MyEnvironment(X='xxx'),
                                    {'O':'ooo'},
                                    't',
                                    ['s1', 's2'])
        be = x.get_build_env()
        assert be == {'O':'ooo', 'X':'xxx'}, be

        env = MyEnvironment(Y='yyy')
        over = {'O':'ooo'}
        x = SCons.Executor.Executor(MyBuilder(env, over), None, {}, 't', 's')
        be = x.get_build_env()
        assert be == {'O':'ooo', 'Y':'yyy'}, be

    def test_get_action_list(self):
        """Test fetching and generating an action list"""
        x = SCons.Executor.Executor('b', 'e', 'o', 't', 's')
        x.action_list = ['aaa']
        al = x.get_action_list(MyNode([], []))
        assert al == ['aaa'], al
        al = x.get_action_list(MyNode(['PRE'], ['POST']))
        assert al == ['PRE', 'aaa', 'POST'], al

        x = SCons.Executor.Executor(MyBuilder('e', 'o'), None, {}, 't', 's')
        al = x.get_action_list(MyNode(['pre'], ['post']))
        assert al == ['pre', 'action1', 'action2', 'post'], al

    def test__call__(self):
        """Test calling an Executor"""
        actions = []
        env = MyEnvironment(CALL='call')
        b = MyBuilder(env, {})
        x = SCons.Executor.Executor(b, None, {}, ['t1', 't2'], ['s1', 's2'])
        def func(action, target, source, env, a=actions):
            a.append(action)
            assert target == ['t1', 't2'], target
            assert source == ['s1', 's2'], source
            assert env == {'CALL':'call'}, env
        x(MyNode(['pre'], ['post']), func)
        assert actions == ['pre', 'action1', 'action2', 'post'], actions

    def test_add_sources(self):
        """Test adding sources to an Executor"""
        x = SCons.Executor.Executor('b', 'e', 'o', 't', ['s1', 's2'])
        assert x.sources == ['s1', 's2'], x.sources
        x.add_sources(['s1', 's2'])
        assert x.sources == ['s1', 's2'], x.sources
        x.add_sources(['s3', 's1', 's4'])
        assert x.sources == ['s1', 's2', 's3', 's4'], x.sources

    def test_get_raw_contents(self):
        """Test fetching the raw signatures contents"""
        env = MyEnvironment(RC='raw contents')

        x = SCons.Executor.Executor(MyBuilder(env, {}), None, {}, ['t'], ['s'])
        x.raw_contents = 'raw raw raw'
        rc = x.get_raw_contents()
        assert rc == 'raw raw raw', rc

        x = SCons.Executor.Executor(MyBuilder(env, {}), None, {}, ['t'], ['s'])
        rc = x.get_raw_contents()
        assert rc == 'RAW action1 action2 t s', rc

    def test_get_contents(self):
        """Test fetching the signatures contents"""
        env = MyEnvironment(C='contents')

        x = SCons.Executor.Executor(MyBuilder(env, {}), None, {}, ['t'], ['s'])
        x.contents = 'contents'
        c = x.get_contents()
        assert c == 'contents', c

        x = SCons.Executor.Executor(MyBuilder(env, {}), None, {}, ['t'], ['s'])
        c = x.get_contents()
        assert c == 'action1 action2 t s', c

    def test_get_timetstamp(self):
        """Test fetching the "timestamp" """
        x = SCons.Executor.Executor('b', 'e', 'o', 't', ['s1', 's2'])
        ts = x.get_timestamp()
        assert ts is None, ts


if __name__ == "__main__":
    suite = unittest.TestSuite()
    tclasses = [ ExecutorTestCase ]
    for tclass in tclasses:
        names = unittest.getTestCaseNames(tclass, 'test_')
        suite.addTests(map(tclass, names))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
