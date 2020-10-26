#!/usr/bin/env python
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

"""
Verify that setting the $TEMPFILEDIR variable will cause
the generated tempfile used for long command lines to be created in specified directory.
And if not specified in one of TMPDIR, TEMP or TMP (based on os' normal usage of such)
"""
from re import escape
import tempfile
import TestSCons
from TestCmd import IS_WINDOWS

test = TestSCons.TestSCons(match=TestSCons.match_re)

test.file_fixture('fixture/SConstruct.tempfiledir', 'SConstruct')

expected_output = r"""Using tempfile __WORKDIR__/my_temp_files/\S+ for command line:
xxx.py foo.out foo.in
xxx.py @__WORKDIR__/my_temp_files/\S+
Using tempfile __TEMPDIR__/\S+ for command line:
xxx.py global_foo.out foo.in
xxx.py @__TEMPDIR__/\S+
"""

if IS_WINDOWS:
    expected_output = expected_output.replace('/','\\\\')
wd_escaped = escape(test.workdir)
td_escaped = escape(tempfile.gettempdir())
expected_output =expected_output.replace("__WORKDIR__", wd_escaped)
expected_output = expected_output.replace("__TEMPDIR__", td_escaped)

test.write('foo.in', "foo.in\n")

test.run(arguments='-n -Q .',
         stdout=expected_output)
# """\
# Using tempfile \\S+ for command line:
# xxx.py foo.out foo.in
# xxx.py \\S+
# """)
#
# try:
#     tempfile = test.stdout().splitlines()[0].split()[2]
# except IndexError:
#     test.fail_test("Unexpected output couldn't find tempfile")
#
# dirname = os.path.basename(os.path.dirname(tempfile))
# test.fail_test('my_temp_files' != dirname, message="Temp file not created in \"my_temp_files\" directory")
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
