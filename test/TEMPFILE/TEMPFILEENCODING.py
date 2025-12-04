#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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
Verify that setting the $TEMPFILEENCODING variable will be used for
encoding the file contents when writing the generated tempfile used
for long command lines.
"""


import TestSCons

test = TestSCons.TestSCons()

test.file_fixture('fixture/SConstruct-tempfile-encoding', 'SConstruct')

expected_pass = """\
Using tempfile \\S+ for command line:
xyz \\S+
scons:.*
"""

expected_fail = """\
tempfile encoding error: \\[{exception}\\] .+
  TempFileMunge encoding: env\\['TEMPFILEENCODING'\\] = {encoding!r}
scons:.*
"""

expected_pass_default = """\
SCons[.]Platform[.]TEMPFILE_DEFAULT_ENCODING = {encoding!r}
""" + expected_pass

expected_fail_default = """\
SCons[.]Platform[.]TEMPFILE_DEFAULT_ENCODING = {encoding!r}
tempfile encoding error: \\[{exception}\\] .+
  TempFileMunge encoding: default = {encoding!r}
scons:.*
"""

for test_encoding, test_tempfileencoding, test_defaultencoding, test_expected in [

    # expected pass
    ('',          False, False, expected_pass),
    ('utf-8',      True, False, expected_pass),
    ('utf-8-sig',  True, False, expected_pass),
    ('utf-16',     True, False, expected_pass),
    ('utf-16',    False,  True, expected_pass_default.format(encoding='utf-16')),

    # expected fail
    ('ascii',    True, False, expected_fail.format(exception='UnicodeEncodeError', encoding='ascii')),
    ('missing',  True, False, expected_fail.format(exception='LookupError', encoding='missing')),
    ('',         True, False, expected_fail.format(exception='LookupError', encoding='')),
    (None,       True, False, expected_fail.format(exception='TypeError', encoding=None)),
    ('ascii',   False,  True, expected_fail_default.format(exception='UnicodeEncodeError', encoding='ascii')),

]:

    args = []
    if test_encoding != "":
        args.append(f'--encoding={test_encoding}')
    if test_tempfileencoding:
        args.append("--set-tempfile-encoding")
    if test_defaultencoding:
        args.append("--set-default-encoding")

    argstr = " ".join(args)

    test.run(
        arguments=f'-n -Q . {argstr}',
        stdout=test_expected,
        match=TestSCons.match_re,
    )

test.pass_test()
