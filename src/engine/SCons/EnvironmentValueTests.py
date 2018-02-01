import unittest

from SCons.EnvironmentValue import EnvironmentValue, ValueTypes
from SCons.EnvironmentValuesTests import TestLiteral


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


if __name__ == '__main__':
    unittest.main()
