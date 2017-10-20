import unittest
import os.path

from SCons.EnvironmentValues import EnvironmentValues, EnvironmentValue, ValueTypes, SubstModes


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

class TestEnvironmentValue(unittest.TestCase):
    """
    Test the class which holds a single environment value
    """

    def test_parse_simple_values(self):
        one = EnvironmentValue('SHLINKCOM',
                               '$LDMODULE -o $TARGET $LDMODULEFLAGS $__LDMODULEVERSIONFLAGS $__RPATH $SOURCES $_LIBDIRFLAGS $_LIBFLAGS')
        self.assertEqual(one._parsed,
                         ['$LDMODULE', ' ', '-o', ' ', '$TARGET', ' ', '$LDMODULEFLAGS', ' ', '$__LDMODULEVERSIONFLAGS',
                          ' ', '$__RPATH', ' ', '$SOURCES', ' ', '$_LIBDIRFLAGS', ' ', '$_LIBFLAGS'])

        self.assertEqual(one.var_type, ValueTypes.PARSED)

        self.assertEqual(one.depends_on,
                         {'LDMODULE', 'TARGET', '__LDMODULEVERSIONFLAGS', 'SOURCES', 'LDMODULEFLAGS', '_LIBFLAGS',
                          '_LIBDIRFLAGS', '__RPATH'},
                         "depends_on:%s\n  (AD:%s)\n  (P:%s)" % (one.depends_on, one.all_dependencies, one._parsed))

    def test_function_call(self):
        one = EnvironmentValue('_LIBFLAGS',
                               '${_stripixes(LIBLINKPREFIX, LIBS, LIBLINKSUFFIX, LIBPREFIXES, LIBSUFFIXES, __env__)}')
        self.assertEqual(one._parsed,
                         ['${_stripixes(LIBLINKPREFIX, LIBS, LIBLINKSUFFIX, LIBPREFIXES, LIBSUFFIXES, __env__)}'])
        self.assertEqual(one.var_type, ValueTypes.PARSED)
        self.assertEqual(one.depends_on,
                         {'LIBLINKSUFFIX', 'LIBPREFIXES', 'LIBLINKPREFIX', 'LIBSUFFIXES', '__env__', 'LIBS',
                          '_stripixes'})

    def test_plain_string_value(self):
        value = '/abc/dev/g++ -o something.obj something.c -DABC'
        one = EnvironmentValue('MYVALUE', value)
        self.assertEqual(one._parsed, [])
        self.assertEqual(one.value, value)
        self.assertEqual(one.var_type, ValueTypes.STRING)
        self.assertEqual(one.depends_on, set())

    def test_plain_string_with_excludes(self):
        value = '/abc/dev/g++ -o something.obj something.c $(-DABC $)'
        one = EnvironmentValue('MYVALUE', value)
        self.assertEqual(one._parsed,
                         ['/abc/dev/g++', ' ', '-o', ' ', 'something.obj', ' ', 'something.c', ' ', '$(', '-DABC', ' ',
                          '$)'])
        self.assertEqual(one.value, value)
        self.assertEqual(one.var_type, ValueTypes.PARSED)
        self.assertEqual(one.depends_on, set())

    def test_list_value(self):
        value = ['gcc', 'g++', 'applelink', 'ar', 'libtool', 'as', 'xcode']
        one = EnvironmentValue('TOOLS', value)
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
        one = EnvironmentValue('MONGO_BUILDINFO_ENVIRONMENT_DATA', value)
        self.assertEqual(one._parsed, [])
        self.assertEqual(one.var_type, ValueTypes.COLLECTION)

        # Not sure this is right, but perhaps we just don't cache these?
        self.assertEqual(one.depends_on, set())

    def test_callable_value(self):
        def foo(target, source, env, for_signature):
            return "bar"

        one = EnvironmentValue('FOO', foo)
        self.assertEqual(one.var_type, ValueTypes.CALLABLE)

        # Test that callable is retrievable and callable and value is proper.
        self.assertEqual(one.value(None, None, None, None), "bar")

    def test_dict_value(self):
        one = EnvironmentValue('ENV', {})

        one['ENV']['BLAH'] = 1

        self.assertEqual(one['ENV']['BLAH'], 1)


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
                                YYY='$Y', Y='Two', YYYY='$YYY')

        # vanilla string should equal itself
        x = env.subst('X')
        self.assertEqual(x, 'One')

        # Single level expansion
        xxx = env.subst('XXX')
        self.assertEqual(xxx, 'One')

        # Double level expansion
        xxxx = env.subst('XXXX')
        self.assertEqual(xxxx, 'One')

        # Now reverse evaluation
        # Double level expansion
        yyyy = env.subst('YYYY')
        self.assertEqual(yyyy, 'Two')

    def test_escape_values(self):
        env = EnvironmentValues(X='One', XX='Two', XXX='$X $($XX$)')

        # vanilla string should equal itself
        x = env.subst('X')
        self.assertEqual(x, 'One')

        # Single level expansion
        xxx = env.subst('XXX')
        self.assertEqual(xxx, 'One Two')

        # Now try getting for signature which should skip escaped part of string
        xxx_sig = env.subst('XXX', raw=SubstModes.FOR_SIGNATURE)
        self.assertEqual(xxx_sig, 'One')  # Should we have trailing space?

    def test_simple_callable_function(self):
        def foo(target, source, env, for_signature):
            return "bar"

        t1 = MyNode('t1')
        t2 = MyNode('t2')
        s1 = MyNode('s1')
        s2 = MyNode('s2')


        # Will expand $BAR to "bar baz"
        env = EnvironmentValues(FOO=foo, BAR="$FOO baz")

        foo = env.subst('FOO',
                        target=[t1, t2],
                        source=[s1, s2])

        self.assertEqual(foo, 'bar')

        bar = env.subst('BAR',
                        target=[t1, t2],
                        source=[s1, s2])
        self.assertEqual(bar, 'bar baz')


if __name__ == '__main__':
    unittest.main()
