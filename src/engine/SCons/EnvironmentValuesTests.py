import unittest
import os.path

from SCons.EnvironmentValues import EnvironmentValues, EnvironmentValue, ValueTypes, SubstModes
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


class TestLiteral(object):
    def __init__(self, literal):
        self.literal = literal

    def __str__(self):
        return self.literal

    def is_literal(self):
        return 1


class TestEnvironmentValue(unittest.TestCase):
    """
    Test the class which holds a single environment value
    """

    def test_parse_simple_values(self):
        one = EnvironmentValue('$LDMODULE -o $TARGET $LDMODULEFLAGS $__LDMODULEVERSIONFLAGS $__RPATH $SOURCES $_LIBDIRFLAGS $_LIBFLAGS')
        self.assertEqual(one._parsed,
                         ['$LDMODULE', ' ', '-o', ' ', '$TARGET', ' ', '$LDMODULEFLAGS', ' ', '$__LDMODULEVERSIONFLAGS',
                          ' ', '$__RPATH', ' ', '$SOURCES', ' ', '$_LIBDIRFLAGS', ' ', '$_LIBFLAGS'])

        self.assertEqual(one.var_type, ValueTypes.PARSED)

        self.assertEqual(one.depends_on,
                         {'LDMODULE', 'TARGET', '__LDMODULEVERSIONFLAGS', 'SOURCES', 'LDMODULEFLAGS', '_LIBFLAGS',
                          '_LIBDIRFLAGS', '__RPATH'},
                         "depends_on:%s\n  (AD:%s)\n  (P:%s)" % (one.depends_on, one.all_dependencies, one._parsed))

    def test_dollar_in_string(self):
        one=EnvironmentValue('$$FFF$HHH')
        self.assertEqual(one._parsed,['$$','FFF','$HHH'])
        self.assertEqual(one.all_dependencies,[(ValueTypes.STRING,'$',0), (ValueTypes.STRING,'FFF',1),
                                               (ValueTypes.VARIABLE_OR_CALLABLE, 'HHH', 2)])
        self.assertEqual(one.depends_on,{'HHH'})

        # import pdb; pdb.set_trace()
        # two=EnvironmentValue('${TARGETS[:]}')

    def test_function_call(self):
        one = EnvironmentValue('${_stripixes(LIBLINKPREFIX, LIBS, LIBLINKSUFFIX, LIBPREFIXES, LIBSUFFIXES, __env__)}')
        self.assertEqual(one._parsed,
                         ['${_stripixes(LIBLINKPREFIX, LIBS, LIBLINKSUFFIX, LIBPREFIXES, LIBSUFFIXES, __env__)}'])
        self.assertEqual(one.var_type, ValueTypes.PARSED)
        self.assertEqual(one.depends_on,
                         {'LIBLINKSUFFIX', 'LIBPREFIXES', 'LIBLINKPREFIX', 'LIBSUFFIXES', '__env__', 'LIBS',
                          '_stripixes'})

    def test_plain_string_value(self):
        value = '/abc/dev/g++ -o something.obj something.c -DABC'
        one = EnvironmentValue(value)
        self.assertEqual(one._parsed, [])
        self.assertEqual(one.value, value)
        self.assertEqual(one.var_type, ValueTypes.STRING)
        self.assertEqual(one.depends_on, set())

    def test_plain_string_with_excludes(self):
        value = '/abc/dev/g++ -o something.obj something.c $(-DABC $)'
        one = EnvironmentValue(value)
        self.assertEqual(one._parsed,
                         ['/abc/dev/g++', ' ', '-o', ' ', 'something.obj', ' ', 'something.c', ' ', '$(', '-DABC', ' ',
                          '$)'])
        self.assertEqual(one.value, value)
        self.assertEqual(one.var_type, ValueTypes.PARSED)
        self.assertEqual(one.depends_on, set())

    def test_list_value(self):
        value = ['gcc', 'g++', 'applelink', 'ar', 'libtool', 'as', 'xcode']
        one = EnvironmentValue(value)
        self.assertEqual(one._parsed, [])
        self.assertEqual(one.value, value)
        self.assertEqual(one.var_type, ValueTypes.COLLECTION)
        self.assertEqual(one.depends_on, set())

    def test_tuple_value(self):
        value = (('distmod', '$MONGO_DISTMOD', True, True), ('distarch', '$MONGO_DISTARCH', True, True),
                 ('cc', '$CC_VERSION', True, False), ('ccflags', '$CCFLAGS', True, False),
                 ('cxx', '$CXX_VERSION', True, False), ('cxxflags', '$CXXFLAGS', True, False),
                 ('linkflags', '$LINKFLAGS', True, False), ('target_arch', '$TARGET_ARCH', True, True),
                 ('target_os', '$TARGET_OS', True, False))
        one = EnvironmentValue(value)
        self.assertEqual(one._parsed, [])
        self.assertEqual(one.var_type, ValueTypes.COLLECTION)

        # Not sure this is right, but perhaps we just don't cache these?
        self.assertEqual(one.depends_on, set())

    def test_callable_value(self):
        def foo(target, source, env, for_signature):
            return "bar"

        one = EnvironmentValue(foo)
        self.assertEqual(one.var_type, ValueTypes.CALLABLE)

        # Test that callable is retrievable and callable and value is proper.
        self.assertEqual(one.value(None, None, None, None), "bar")

    def test_dict_value(self):
        one = EnvironmentValue({})

        one['ENV'] = {}
        one['ENV']['BLAH'] = 1

        self.assertEqual(one['ENV']['BLAH'], 1)

    def test_literal_value(self):
        """ Check handling a Literal() value (One which should not be recursively evaluated)"""
        one = EnvironmentValue(TestLiteral('$XXX'))
        self.assertEqual(one.var_type, ValueTypes.LITERAL,
                         "Should be a Literal not:%s"%ValueTypes.enum_name(one.var_type))
        self.assertEqual(one.cached, ('$XXX','$XXX'),
                         "Cached value should be tuple with two elements of $XXX not:%s"%repr(one.cached))

    def test_none_value(self):
        """ Check handling a Literal() value (One which should not be recursively evaluated)"""
        one = EnvironmentValue(None)
        self.assertEqual(one.var_type, ValueTypes.NONE,
                         "Should be a NONE not:%s"%ValueTypes.enum_name(one.var_type))
        self.assertEqual(one.cached, ('',''),
                         "Cached value should be tuple with two elements of None not:%s"%repr(one.cached))

    def test_evalable_value(self):
        """ Check handing  ${TARGETS[:]} ${SOURCES[0]}"""
        one = EnvironmentValue('test ${TARGETS[:]} ${SOURCES[0]}')
        self.assertEqual(one._parsed, ['test', ' ', '${TARGETS[:]}', ' ', '${SOURCES[0]}'])
        self.assertEqual(one.all_dependencies,
                         [(1, 'test', 0), (1, ' ', 1),
                          (15, 'TARGETS[:]', 2), (1, ' ', 3), (15, 'SOURCES[0]', 4)] )


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
        x = env.subst('X', env)
        self.assertEqual(x, 'One')

        # Single level expansion
        xxx = env.subst('XXX', env)
        self.assertEqual(xxx, 'One')

        # Double level expansion
        xxxx = env.subst('XXXX', env)
        self.assertEqual(xxxx, 'One')

        # Now reverse evaluation
        # Double level expansion
        yyyy = env.subst('YYYY', env)
        self.assertEqual(yyyy, 'Two')

        # Now eval something who value doesn't exist
        zzzz = env.subst('ZZZZ', env)
        self.assertEqual(zzzz,'')

        # Now eval something who value doesn't exist
        zzzy = env.subst('ZZZZ', env)
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
        x = env.subst('X', env)
        self.assertEqual(x, 'One')

        # Single level expansion
        xxx = env.subst('XXX', env)
        self.assertEqual(xxx, 'One Two')

        # Now try getting for signature which should skip escaped part of string
        xxx_sig = env.subst('XXX', env, mode=SubstModes.FOR_SIGNATURE)
        self.assertEqual(xxx_sig, 'One')  # Should we have trailing space?

    def test_simple_callable_function(self):
        def foo(target, source, env, for_signature):
            return "bar"

        t1 = MyNode('t1')
        t2 = MyNode('t2')
        s1 = MyNode('s1')
        s2 = MyNode('s2')

        # Will expand $BAR to "bar baz"
        env = EnvironmentValues(FOO=foo, BAR="$FOO baz", CMDGEN1=CmdGen1, CMDGEN2=CmdGen2)

        foo = env.subst('FOO', env,
                        target=[t1, t2],
                        source=[s1, s2])

        self.assertEqual(foo, 'bar')

        bar = env.subst('BAR', env,
                        target=[t1, t2],
                        source=[s1, s2])
        self.assertEqual(bar, 'bar baz')

        _t = DummyNode('t')
        _s = DummyNode('s')

        # CMDGEN1 calls CmdGen2
        xar = env.subst('$CMDGEN1', env,
                        target=_t,
                        source=_s)
        self.assertEqual(xar, 'bar bar with spaces.out')

    def test_setitem(self):
        env = EnvironmentValues(X='One', XX='Two', XXX='$X $($XX$)')

        # vanilla string should equal itself
        x = env.subst('X', env)
        self.assertEqual(x, 'One')

        env['Y'] = '$X'

        xxx = env.subst('XXX', env)

        # Change the value to XX and make sure the value of XXX
        # changed
        env['XX'] = 'BLAH'
        xxx_2 = env.subst('XXX', env)
        self.assertNotEqual(xxx, xxx_2)
        self.assertEqual(xxx_2, "One BLAH")

        # now set XX to a function and verify that the value changed
        # and that the value is correct with the new function
        def foo(target, source, env, for_signature):
            return "bar"
        env['XX'] = foo
        xxx_3 = env.subst('XXX', env)
        # print("1:%s 2:%s 3:%s"%(xxx, xxx_2, xxx_3))
        self.assertNotEqual(xxx_3, xxx_2)
        self.assertEqual(xxx_3, 'One bar')


if __name__ == '__main__':
    unittest.main()
