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

import sys
import unittest

import SCons.Executor


class MyEnvironment(object):
    def __init__(self, **kw):
        self._dict = {}
        self._dict.update(kw)
    def __getitem__(self, key):
        return self._dict[key]
    def Override(self, overrides):
        d = self._dict.copy()
        d.update(overrides)
        return MyEnvironment(**d)
    def _update(self, dict):
        self._dict.update(dict)

class MyAction(object):
    def __init__(self, actions=['action1', 'action2']):
        self.actions = actions
    def __call__(self, target, source, env, **kw):
        for action in self.actions:
            action(target, source, env, **kw)
    def genstring(self, target, source, env):
        return ' '.join(['GENSTRING'] + list(map(str, self.actions)) + target + source)
    def get_contents(self, target, source, env):
        return b' '.join(
            [SCons.Util.to_bytes(aa) for aa in self.actions] + 
            [SCons.Util.to_bytes(tt) for tt in target] +
            [SCons.Util.to_bytes(ss) for ss in source]
        )
    def get_implicit_deps(self, target, source, env):
        return []

class MyBuilder(object):
    def __init__(self, env, overrides):
        self.env = env
        self.overrides = overrides
        self.action = MyAction()

class MyNode(object):
    def __init__(self, name=None, pre=[], post=[]):
        self.name = name
        self.implicit = []
        self.pre_actions = pre
        self.post_actions = post
        self.missing_val = None
        self.always_build = False
        self.up_to_date = False

    def __str__(self):
        return self.name

    def build(self):
        executor = SCons.Executor.Executor(MyAction(self.pre_actions +
                                                    [self.builder.action] +
                                                    self.post_actions),
                                           self.builder.env,
                                           [],
                                           [self],
                                           ['s1', 's2'])
        executor(self)
    def get_env_scanner(self, env, kw):
        return MyScanner('dep-')
    def get_implicit_deps(self, env, scanner, path, kw={}):
        if not scanner:
            scanner = self.get_env_scanner(env, kw)
        return [scanner.prefix + str(self)]
    def add_to_implicit(self, deps):
        self.implicit.extend(deps)
    def missing(self):
        return self.missing_val
    def calc_signature(self, calc):
        return 'cs-'+calc+'-'+self.name
    def disambiguate(self):
        return self

    def is_up_to_date(self):
        return self.up_to_date

class MyScanner(object):
    def __init__(self, prefix):
        self.prefix = prefix
    def path(self, env, cwd, target, source):
        return ()
    def select(self, node):
        return self

class ExecutorTestCase(unittest.TestCase):

    def test__init__(self):
        """Test creating an Executor"""
        source_list = ['s1', 's2']
        x = SCons.Executor.Executor('a', 'e', ['o'], 't', source_list)
        assert x.action_list == ['a'], x.action_list
        assert x.env == 'e', x.env
        assert x.overridelist == ['o'], x.overridelist
        targets = x.get_all_targets()
        assert targets == ['t'], targets
        source_list.append('s3')
        sources = x.get_all_sources()
        assert sources == ['s1', 's2'], sources
        try:
            x = SCons.Executor.Executor(None, 'e', ['o'], 't', source_list)
        except SCons.Errors.UserError:
            pass
        else:
            raise Exception("Did not catch expected UserError")

    def test__action_list(self):
        """Test the {get,set}_action_list() methods"""
        x = SCons.Executor.Executor('a', 'e', 'o', 't', ['s1', 's2'])

        l = x.get_action_list()
        assert l == ['a'], l

        x.add_pre_action('pre')
        x.add_post_action('post')
        l = x.get_action_list()
        assert l == ['pre', 'a', 'post'], l

        x.set_action_list('b')
        l = x.get_action_list()
        assert l == ['pre', 'b', 'post'], l

        x.set_action_list(['c'])
        l = x.get_action_list()
        assert l == ['pre', 'c', 'post'], l

    def test_get_build_env(self):
        """Test fetching and generating a build environment"""
        x = SCons.Executor.Executor(MyAction(), MyEnvironment(e=1), [],
                                    't', ['s1', 's2'])
        x.env = MyEnvironment(eee=1)
        be = x.get_build_env()
        assert be['eee'] == 1, be

        env = MyEnvironment(X='xxx')
        x = SCons.Executor.Executor(MyAction(),
                                    env,
                                    [{'O':'o2'}],
                                    't',
                                    ['s1', 's2'])
        be = x.get_build_env()
        assert be['O'] == 'o2', be['O']
        assert be['X'] == 'xxx', be['X']

        env = MyEnvironment(Y='yyy')
        overrides = [{'O':'ob3'}, {'O':'oo3'}]
        x = SCons.Executor.Executor(MyAction(), env, overrides, ['t'], ['s'])
        be = x.get_build_env()
        assert be['O'] == 'oo3', be['O']
        assert be['Y'] == 'yyy', be['Y']
        overrides = [{'O':'ob3'}]
        x = SCons.Executor.Executor(MyAction(), env, overrides, ['t'], ['s'])
        be = x.get_build_env()
        assert be['O'] == 'ob3', be['O']
        assert be['Y'] == 'yyy', be['Y']

    def test_get_build_scanner_path(self):
        """Test fetching the path for the specified scanner."""
        t = MyNode('t')
        t.cwd = 'here'
        x = SCons.Executor.Executor(MyAction(),
                                    MyEnvironment(SCANNERVAL='sss'),
                                    [],
                                    [t],
                                    ['s1', 's2'])

        class LocalScanner(object):
            def path(self, env, dir, target, source):
                target = list(map(str, target))
                source = list(map(str, source))
                return "scanner: %s, %s, %s, %s" % (env['SCANNERVAL'], dir, target, source)
        s = LocalScanner()

        p = x.get_build_scanner_path(s)
        assert p == "scanner: sss, here, ['t'], ['s1', 's2']", p

    def test_get_kw(self):
        """Test the get_kw() method"""
        t = MyNode('t')
        x = SCons.Executor.Executor(MyAction(),
                                    MyEnvironment(),
                                    [],
                                    [t],
                                    ['s1', 's2'],
                                    builder_kw={'X':1, 'Y':2})
        kw = x.get_kw()
        assert kw == {'X':1, 'Y':2, 'executor':x}, kw
        kw = x.get_kw({'Z':3})
        assert kw == {'X':1, 'Y':2, 'Z':3, 'executor':x}, kw
        kw = x.get_kw({'X':4})
        assert kw == {'X':4, 'Y':2, 'executor':x}, kw

    def test__call__(self):
        """Test calling an Executor"""
        result = []
        def pre(target, source, env, result=result, **kw):
            result.append('pre')
        def action1(target, source, env, result=result, **kw):
            result.append('action1')
        def action2(target, source, env, result=result, **kw):
            result.append('action2')
        def post(target, source, env, result=result, **kw):
            result.append('post')

        env = MyEnvironment()
        a = MyAction([action1, action2])
        t = MyNode('t')

        x = SCons.Executor.Executor(a, env, [], [t], ['s1', 's2'])
        x.add_pre_action(pre)
        x.add_post_action(post)
        x(t)
        assert result == ['pre', 'action1', 'action2', 'post'], result
        del result[:]

        def pre_err(target, source, env, result=result, **kw):
            result.append('pre_err')
            return 1

        x = SCons.Executor.Executor(a, env, [], [t], ['s1', 's2'])
        x.add_pre_action(pre_err)
        x.add_post_action(post)
        try:
            x(t)
        except SCons.Errors.BuildError:
            pass
        else:
            raise Exception("Did not catch expected BuildError")
        assert result == ['pre_err'], result
        del result[:]

    def test_cleanup(self):
        """Test cleaning up an Executor"""
        orig_env = MyEnvironment(e=1)
        x = SCons.Executor.Executor('b', orig_env, [{'o':1}],
                                    't', ['s1', 's2'])

        be = x.get_build_env()
        assert be['e'] == 1, be['e']
        
        x.cleanup()

        x.env = MyEnvironment(eee=1)
        be = x.get_build_env()
        assert be['eee'] == 1, be['eee']

        x.cleanup()

        be = x.get_build_env()
        assert be['eee'] == 1, be['eee']

    def test_add_sources(self):
        """Test adding sources to an Executor"""
        x = SCons.Executor.Executor('b', 'e', 'o', 't', ['s1', 's2'])
        sources = x.get_all_sources()
        assert sources == ['s1', 's2'], sources

        x.add_sources(['s1', 's2'])
        sources = x.get_all_sources()
        assert sources == ['s1', 's2'], sources

        x.add_sources(['s3', 's1', 's4'])
        sources = x.get_all_sources()
        assert sources == ['s1', 's2', 's3', 's4'], sources

    def test_get_sources(self):
        """Test getting sources from an Executor"""
        x = SCons.Executor.Executor('b', 'e', 'o', 't', ['s1', 's2'])
        sources = x.get_sources()
        assert sources == ['s1', 's2'], sources

        x.add_sources(['s1', 's2'])
        sources = x.get_sources()
        assert sources == ['s1', 's2'], sources

        x.add_sources(['s3', 's1', 's4'])
        sources = x.get_sources()
        assert sources == ['s1', 's2', 's3', 's4'], sources

    def test_prepare(self):
        """Test the Executor's prepare() method"""
        env = MyEnvironment()
        t1 = MyNode('t1')
        s1 = MyNode('s1')
        s2 = MyNode('s2')
        s3 = MyNode('s3')
        x = SCons.Executor.Executor('b', env, [{}], [t1], [s1, s2, s3])

        s2.missing_val = True

        try:
            r = x.prepare()
        except SCons.Errors.StopError as e:
            assert str(e) == "Source `s2' not found, needed by target `t1'.", e
        else:
            raise AssertionError("did not catch expected StopError: %s" % r)

    def test_add_pre_action(self):
        """Test adding pre-actions to an Executor"""
        x = SCons.Executor.Executor('b', 'e', 'o', 't', ['s1', 's2'])
        x.add_pre_action('a1')
        assert x.pre_actions == ['a1']
        x.add_pre_action('a2')
        assert x.pre_actions == ['a1', 'a2']

    def test_add_post_action(self):
        """Test adding post-actions to an Executor"""
        x = SCons.Executor.Executor('b', 'e', 'o', 't', ['s1', 's2'])
        x.add_post_action('a1')
        assert x.post_actions == ['a1']
        x.add_post_action('a2')
        assert x.post_actions == ['a1', 'a2']

    def test___str__(self):
        """Test the __str__() method"""
        env = MyEnvironment(S='string')

        x = SCons.Executor.Executor(MyAction(), env, [], ['t'], ['s'])
        c = str(x)
        assert c == 'GENSTRING action1 action2 t s', c

        x = SCons.Executor.Executor(MyAction(), env, [], ['t'], ['s'])
        x.add_pre_action(MyAction(['pre']))
        x.add_post_action(MyAction(['post']))
        c = str(x)
        expect = 'GENSTRING pre t s\n' + \
                 'GENSTRING action1 action2 t s\n' + \
                 'GENSTRING post t s'
        assert c == expect, c

    def test_nullify(self):
        """Test the nullify() method"""
        env = MyEnvironment(S='string')

        result = []
        def action1(target, source, env, result=result, **kw):
            result.append('action1')

        env = MyEnvironment()
        a = MyAction([action1])
        x = SCons.Executor.Executor(a, env, [], ['t1', 't2'], ['s1', 's2'])

        x(MyNode('', [], []))
        assert result == ['action1'], result
        s = str(x)
        assert s[:10] == 'GENSTRING ', s

        del result[:]
        x.nullify()

        assert result == [], result
        x(MyNode('', [], []))
        assert result == [], result
        s = str(x)
        assert s == '', s

    def test_get_contents(self):
        """Test fetching the signatures contents"""
        env = MyEnvironment(C='contents')

        x = SCons.Executor.Executor(MyAction(), env, [], ['t'], ['s'])
        c = x.get_contents()
        assert c == b'action1 action2 t s', c

        x = SCons.Executor.Executor(MyAction(actions=['grow']), env, [],
                                    ['t'], ['s'])
        x.add_pre_action(MyAction(['pre']))
        x.add_post_action(MyAction(['post']))
        c = x.get_contents()
        assert c == b'pre t sgrow t spost t s', c

    def test_get_timestamp(self):
        """Test fetching the "timestamp" """
        x = SCons.Executor.Executor('b', 'e', 'o', 't', ['s1', 's2'])
        ts = x.get_timestamp()
        assert ts == 0, ts

    def test_scan_targets(self):
        """Test scanning the targets for implicit dependencies"""
        env = MyEnvironment(S='string')
        t1 = MyNode('t1')
        t2 = MyNode('t2')
        sources = [MyNode('s1'), MyNode('s2')]
        x = SCons.Executor.Executor(MyAction(), env, [{}], [t1, t2], sources)

        deps = x.scan_targets(None)
        assert t1.implicit == ['dep-t1', 'dep-t2'], t1.implicit
        assert t2.implicit == ['dep-t1', 'dep-t2'], t2.implicit

        t1.implicit = []
        t2.implicit = []

        deps = x.scan_targets(MyScanner('scanner-'))
        assert t1.implicit == ['scanner-t1', 'scanner-t2'], t1.implicit
        assert t2.implicit == ['scanner-t1', 'scanner-t2'], t2.implicit

    def test_scan_sources(self):
        """Test scanning the sources for implicit dependencies"""
        env = MyEnvironment(S='string')
        t1 = MyNode('t1')
        t2 = MyNode('t2')
        sources = [MyNode('s1'), MyNode('s2')]
        x = SCons.Executor.Executor(MyAction(), env, [{}], [t1, t2], sources)

        deps = x.scan_sources(None)
        assert t1.implicit == ['dep-s1', 'dep-s2'], t1.implicit
        assert t2.implicit == ['dep-s1', 'dep-s2'], t2.implicit

        t1.implicit = []
        t2.implicit = []

        deps = x.scan_sources(MyScanner('scanner-'))
        assert t1.implicit == ['scanner-s1', 'scanner-s2'], t1.implicit
        assert t2.implicit == ['scanner-s1', 'scanner-s2'], t2.implicit

    def test_get_unignored_sources(self):
        """Test fetching the unignored source list"""
        env = MyEnvironment()
        s1 = MyNode('s1')
        s2 = MyNode('s2')
        s3 = MyNode('s3')
        x = SCons.Executor.Executor('b', env, [{}], [], [s1, s2, s3])

        r = x.get_unignored_sources(None, [])
        assert r == [s1, s2, s3], list(map(str, r))

        r = x.get_unignored_sources(None, [s2])
        assert r == [s1, s3], list(map(str, r))

        r = x.get_unignored_sources(None, [s1, s3])
        assert r == [s2], list(map(str, r))

    def test_changed_sources_for_alwaysBuild(self):
        """
        Ensure if a target is marked always build that the sources are always marked changed sources
        :return:
        """
        env = MyEnvironment()
        s1 = MyNode('s1')
        s2 = MyNode('s2')
        t1 = MyNode('t1')
        t1.up_to_date = True
        t1.always_build = True

        x = SCons.Executor.Executor('b', env, [{}], [t1], [s1, s2])

        changed_sources = x._get_changed_sources()
        assert changed_sources == [s1, s2], "If target marked AlwaysBuild sources should always be marked changed"




if __name__ == "__main__":
    unittest.main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
