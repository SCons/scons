#!/usr/bin/env python
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
import re

import TestSCons

_python_ = TestSCons._python_
_exe = TestSCons._exe

test = TestSCons.TestSCons()

#  Test issue # 2580
test.dir_fixture('applelink_image')
test.run(arguments='-f SConstruct_gh2580 -Q -n', stdout='gcc -o foo.o -c -Fframeworks foo.c\n')

# Now test combinations of SHLIBVERSION, APPLELINK_CURRENT_VERSION, APPLELINK_COMPATIBILITY_VERSION

if sys.platform == 'darwin':
    extra_flags = ''
else:
    extra_flags = ' -n '

for SHLIBVERSION, APPLELINK_CURRENT_VERSION, APPLELINK_COMPATIBILITY_VERSION, should_error in [
    ('1.2.3', '', '', False),
    ('1.2.3', '9.9.9', '9.9.0', False),
    ('99999.2.3', '', '', 'AppleLinkInvalidCurrentVersionException'),
    ('1.2.3', '9.9.999', '9.9.0', 'AppleLinkInvalidCurrentVersionException'),
    ('1.2.3', '9.9.9', '9.999.0', 'AppleLinkInvalidCompatibilityVersionException'),
    ('1.2.3', '9.9.9', '99999.99.0', 'AppleLinkInvalidCompatibilityVersionException'),
]:
    if not APPLELINK_CURRENT_VERSION:
        APPLELINK_CURRENT_VERSION = SHLIBVERSION
    if not APPLELINK_COMPATIBILITY_VERSION:
        APPLELINK_COMPATIBILITY_VERSION = '.'.join(APPLELINK_CURRENT_VERSION.split('.', 2)[:2] + ['0'])

    if not should_error:
        expected_stdout = r"^.+ -dynamiclib -Wl,-current_version,{APPLELINK_CURRENT_VERSION} -Wl,-compatibility_version,{APPLELINK_COMPATIBILITY_VERSION}.+".format(
            **locals())
        expected_stderr = None
        expected_status = 0
    else:
        expected_stdout = None
        expected_stderr = r"^.+{should_error}.+".format(**locals())
        expected_status = 2

    test.run(
        arguments='{extra_flags} -f SConstruct_CurVers_CompatVers SHLIBVERSION={SHLIBVERSION} APPLELINK_CURRENT_VERSION={APPLELINK_CURRENT_VERSION} APPLELINK_COMPATIBILITY_VERSION={APPLELINK_COMPATIBILITY_VERSION}'.format(
            **locals()),
        stdout=expected_stdout,
        stderr=expected_stderr,
        match=TestSCons.match_re_dotall,
        status=expected_status)

    if not (should_error or extra_flags):
        # Now run otool -L to get the compat and current version info and verify it's correct in the library.
        # We expect output such as this
        # libfoo.1.2.3.dylib:
        # > 	libfoo.1.2.3.dylib (compatibility version 1.1.99, current version 9.9.9)
        # > 	/usr/lib/libSystem.B.dylib (compatibility version 1.0.0, current version 1252.50.4)
        # otool_output = "libfoo.{SHLIBVERSION}.dylib:\n\tlibfoo.{SHLIBVERSION}.dylib (compatibility version {APPLELINK_COMPATIBILITY_VERSION}, current version {APPLELINK_CURRENT_VERSION})\n\t/usr/lib/libSystem.B.dylib (compatibility version 1.0.0, current version 1252.50.4)\n".format(
        #     **locals())
        otool_output = "libfoo.{SHLIBVERSION}.dylib:\n\tlibfoo.{SHLIBVERSION}.dylib (compatibility version {APPLELINK_COMPATIBILITY_VERSION}, current version {APPLELINK_CURRENT_VERSION})\n\t/usr/lib/libSystem.B.dylib (compatibility version 1.0.0, current version REPLACEME)\n".format(**locals())
        otool_output = re.escape(otool_output)
        otool_output = otool_output.replace('REPLACEME',r'\d+\.\d+\.\d+')


        test.run(program='/usr/bin/otool', arguments='-L libfoo.%s.dylib' % SHLIBVERSION, stdout=otool_output, match=TestSCons.match_re_dotall)

# Now test that None in APPLELINK_CURRENT_VERSION or APPLELINK_COMPATIBILITY_VERSION will skip
# generating their relevant linker command line flag.
for SHLIBVERSION, \
    APPLELINK_CURRENT_VERSION, APPLELINK_COMPATIBILITY_VERSION, \
    APPLELINK_NO_CURRENT_VERSION, APPLELINK_NO_COMPATIBILITY_VERSION in [
    ('1.2.3', 0, 0, 0, 1),
    ('1.2.3', 0, 0, 1, 0),
    ('1.2.3', 0, 0, 1, 1),

]:

    if not APPLELINK_CURRENT_VERSION:
        APPLELINK_CURRENT_VERSION = SHLIBVERSION
    if not APPLELINK_COMPATIBILITY_VERSION:
        APPLELINK_COMPATIBILITY_VERSION = '.'.join(APPLELINK_CURRENT_VERSION.split('.', 2)[:2] + ['0'])

    test.run(
        arguments='{extra_flags} -f SConstruct_CurVers_CompatVers SHLIBVERSION={SHLIBVERSION} '
                  'APPLELINK_CURRENT_VERSION={APPLELINK_CURRENT_VERSION} '
                  'APPLELINK_COMPATIBILITY_VERSION={APPLELINK_COMPATIBILITY_VERSION} '
                  'APPLELINK_NO_CURRENT_VERSION={APPLELINK_NO_CURRENT_VERSION} '
                  'APPLELINK_NO_COMPATIBILITY_VERSION={APPLELINK_NO_COMPATIBILITY_VERSION} '.format(
            **locals()))

    if APPLELINK_NO_CURRENT_VERSION:
        # Should not contain -Wl,-current_version
        test.must_not_contain_lines(test.stdout(),
                                    ['-Wl,-current_version'])
    else:
        # Should contain -Wl,-current_version,{APPLELINK_CURRENT_VERSION}
        test.must_contain_all_lines(test.stdout(),
                                    ['-Wl,-current_version,{APPLELINK_CURRENT_VERSION}'.format(**locals()), 'libfoo.4.dynlib'])

    if APPLELINK_NO_COMPATIBILITY_VERSION:
        # Should not contain -Wl,-compatibility_version
        test.must_not_contain_lines(test.stdout(),
                                    ['-Wl,-compatibility_version'])
    else:
        # Should contain -Wl,-compatibility_version,{APPLELINK_COMPATIBILITY_VERSION}
        test.must_contain_all_lines(test.stdout(),
                                    ['-Wl,-compatibility_version,{APPLELINK_COMPATIBILITY_VERSION}'.format(**locals()), 'libfoo.4.dynlib'])

    if not extra_flags:
        # Now run otool -L to get the compat and current version info and verify it's correct in the library.
        # We expect output such as this
        # libfoo.1.2.3.dylib:
        # > 	libfoo.1.2.3.dylib (compatibility version 1.1.99, current version 9.9.9)
        # > 	/usr/lib/libSystem.B.dylib (compatibility version 1.0.0, current version #.#.#)
        if APPLELINK_NO_CURRENT_VERSION:
            APPLELINK_CURRENT_VERSION = '0.0.0'
        if APPLELINK_NO_COMPATIBILITY_VERSION:
            APPLELINK_COMPATIBILITY_VERSION = '0.0.0'
        otool_output = "libfoo.{SHLIBVERSION}.dylib:\n\tlibfoo.{SHLIBVERSION}.dylib (compatibility version {APPLELINK_COMPATIBILITY_VERSION}, current version {APPLELINK_CURRENT_VERSION})\n\t/usr/lib/libSystem.B.dylib (compatibility version 1.0.0, current version REPLACEME)\n".format(
            **locals())
        otool_output = re.escape(otool_output).replace('REPLACEME',r'\d+\.\d+\.\d+')

        test.run(program='/usr/bin/otool', arguments='-L libfoo.%s.dylib' % SHLIBVERSION, stdout=otool_output, match=TestSCons.match_re_dotall)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
