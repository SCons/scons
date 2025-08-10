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

SCONSTRUCT_TEMPLATE="""
import SCons.Platform

command = 'xyz ./test€/file.c'
encoding = {encoding!r}

tempfileencoding = {tempfileencoding}
defaultencoding = {defaultencoding}

DefaultEnvironment()

if defaultencoding:
    SCons.Platform.TEMPFILE_DEFAULT_ENCODING = encoding
    print("SCons.Platform.TEMPFILE_DEFAULT_ENCODING = {encoding!r}")

env = Environment(
    tools=[],
    MAXLINELENGTH=2,
)

if tempfileencoding:
    env['TEMPFILEENCODING'] = encoding

tfm = SCons.Platform.TempFileMunge(command)

try:
    tfm(None, None, env, 0)
except SCons.Platform.TempFileEncodeError as e:
    print(str(e))
"""

expected_pass = """\
Using tempfile \\S+ for command line:
xyz \\S+
scons\:.*
"""

expected_fail = """\
TempFileEncodeError: \[{exception}\] .+
  TempFileMunge encoding\: env\['TEMPFILEENCODING'\] = {encoding!r}
scons\:.*
"""

expected_pass_default = """\
SCons\.Platform\.TEMPFILE_DEFAULT_ENCODING = {encoding!r}
""" + expected_pass

expected_fail_default = """\
SCons\.Platform\.TEMPFILE_DEFAULT_ENCODING = {encoding!r}
TempFileEncodeError: \[{exception}\] .+
  TempFileMunge encoding\: default = {encoding!r}
scons\:.*
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

    sconstruct = SCONSTRUCT_TEMPLATE.format(
        encoding = test_encoding,
        tempfileencoding = test_tempfileencoding,
        defaultencoding = test_defaultencoding,
    )
    
    test.write('SConstruct', sconstruct)

    test.run(
        arguments='-n -Q .',
        stdout=test_expected,
        match=TestSCons.match_re,
    )

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
