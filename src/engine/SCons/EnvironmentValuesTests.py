import unittest
import os.path

from SCons.EnvironmentValues import EnvironmentValues, SubstModes
from SCons.EnvironmentValuesSubstTests import CmdGen1, CmdGen2


class DummyNode(object):
    """Simple node work-alike."""
    def __init__(self, name):
        self.name = os.path.normpath(name)

    def __str__(self):
        return self.name

    def is_literal(self):
        return 1

    def rfile(self):
        return self

    def get_subst_proxy(self):
        return self


class MyNode(DummyNode):
    """Simple node work-alike with some extra stuff for testing."""

    def __init__(self, name):
        DummyNode.__init__(self, name)

        class Attribute(object):
            pass

        self.attribute = Attribute()
        self.attribute.attr1 = 'attr$1-' + os.path.basename(name)
        self.attribute.attr2 = 'attr$2-' + os.path.basename(name)

    def get_stuff(self, extra):
        return self.name + extra

    foo = 1


class TestEnvironmentValues(unittest.TestCase):
    def test_simple_environmentValues(self):
        """Test comparing SubstitutionEnvironments
        """

        env1 = EnvironmentValues(XXX='x')
        self.assertEqual(list(env1.values.keys()), ['XXX'])
        self.assertEqual(env1.values['XXX'].depends_on, set())

        env2 = EnvironmentValues(XXX='x', XX="$X", X1="${X}", X2="$($X$)")
        self.assertEqual(sorted(env2.values.keys()), sorted(['X2', 'XX', 'X1', 'XXX']))

    def test_expanding_values(self):
        env = EnvironmentValues(XXX='$X', X='One', XXXX='$XXX',
                                YYY='$Y', Y='Two', YYYY='$YYY',
                                ZZZZ='$Z', ZZZY="$Z $Y")

        # vanilla string should equal itself
        x = env.subst('$X', env)
        self.assertEqual(x, 'One')

        # Single level expansion
        xxx = env.subst('$XXX', env)
        self.assertEqual(xxx, 'One')

        # Double level expansion
        xxxx = env.subst('$XXXX', env)
        self.assertEqual(xxxx, 'One')

        # Now reverse evaluation
        # Double level expansion
        yyyy = env.subst('$YYYY', env)
        self.assertEqual(yyyy, 'Two')

        # Now eval something who value doesn't exist
        zzzz = env.subst('$ZZZZ', env)
        self.assertEqual(zzzz,'')

        # Now eval something who value doesn't exist
        zzzy = env.subst('$ZZZZ', env)
        self.assertEqual(zzzy,'')

        # Test 10 levels deep.
        env['AAA_0'] = '$X'
        for i in range(1,10):
            env['AAA_%d'%i] = '$AAA_%d'%(i-1)
        ten_levels = env.subst('$AAA_9', env)
        self.assertEqual(ten_levels, 'One')

    def test_escape_values(self):
        env = EnvironmentValues(X='One', XX='Two', XXX='$X $($XX$)')

        # vanilla string should equal itself
        x = env.subst('$X', env)
        self.assertEqual(x, 'One')

        # Single level expansion
        xxx = env.subst('$XXX', env)
        self.assertEqual(xxx, 'One Two', "Should have been 'One Two' Was '%s'"%xxx)

        # Now try getting for signature which should skip escaped part of string
        xxx_sig = env.subst('$XXX', env, mode=SubstModes.FOR_SIGNATURE)
        self.assertEqual(xxx_sig, 'One', "Should have been 'One' Was '%s'"%xxx_sig)  # Should we have trailing space?

    def test_simple_callable_function(self):
        def foo(target, source, env, for_signature):
            return "bar"

        t1 = MyNode('t1')
        t2 = MyNode('t2')
        s1 = MyNode('s1')
        s2 = MyNode('s2')

        # CmdGen1 (a normal function) returns a string to call CmdGen2. CmdGen2 is a callable class.
        env = EnvironmentValues(FOO=foo, BAR="$FOO baz", CMDGEN1=CmdGen1, CMDGEN2=CmdGen2)

        foo = env.subst('$FOO', env,
                        target=[t1, t2],
                        source=[s1, s2])

        self.assertEqual(foo, 'bar')

        # Will expand $BAR to "bar baz"
        bar = env.subst('$BAR', env,
                        target=[t1, t2],
                        source=[s1, s2])
        self.assertEqual(bar, 'bar baz')

        _t = DummyNode('t')
        _s = DummyNode('s')

        # CMDGEN1 calls CmdGen2
        xar = env.subst('$CMDGEN1', env,
                        target=_t,
                        source=_s)
        self.assertEqual(xar, 'foo bar baz')

    def test_callable_class(self):
        """ Test subst()'ing a callable class"""

        class CallableClass(object):
            def __init__(self, mystr):
                self.mystr = mystr

            def __call__(self, target, source, env, for_signature):
                assert str(target) == 't1', target
                assert str(source) == 's1', source
                return [self.mystr, '-Ran']

        t1 = MyNode('t1')
        s1 = MyNode('s1')

        # CmdGen1 (a normal function) returns a string to call CmdGen2. CmdGen2 is a callable class.
        env = EnvironmentValues(FOO="${CallMe(\'blah\')}", CallMe=CallableClass)

        foo = env.subst('$FOO', env,
                        target=t1,
                        source=s1)

        self.assertEqual(foo, 'blah -Ran')

    def test_setitem(self):
        env = EnvironmentValues(X='One', XX='Two', XXX='$X $($XX$)')

        # vanilla string should equal itself
        x = env.subst('$X', env)
        self.assertEqual(x, 'One')

        env['Y'] = '$X'

        xxx = env.subst('$XXX', env)

        # Change the value to XX and make sure the value of XXX
        # changed
        env['XX'] = 'BLAH'
        xxx_2 = env.subst('$XXX', env)
        self.assertNotEqual(xxx, xxx_2)
        self.assertEqual(xxx_2, "One BLAH", "Should have been 'One BLAH' Was '%s'"%xxx_2)

        # now set XX to a function and verify that the value changed
        # and that the value is correct with the new function
        def foo(target, source, env, for_signature):
            return "bar"

        env['XX'] = foo

        xxx_3 = env.subst('$XXX', env)
        # print("1:%s 2:%s 3:%s"%(xxx, xxx_2, xxx_3))
        self.assertNotEqual(xxx_3, xxx_2)
        self.assertEqual(xxx_3, 'One bar', "Should have been 'One bar' Was '%s'"%xxx_3)


if __name__ == '__main__':
    unittest.main()
