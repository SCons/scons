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
Test that invalid SetOption calls generate expected errors.
"""

import TestSCons

test = TestSCons.TestSCons()

badopts = (
    ("no_such_var", True, "This option is not settable from a SConscript file: no_such_var"),
    ("num_jobs", -22, "A positive integer is required: -22"),
    ("max_drift", "'Foo'", "An integer is required: 'Foo'"),
    ("duplicate", "'cookie'", "Not a valid duplication style: cookie"),
    ("diskcheck", "'off'", "Not a valid diskcheck value: off"),
    ("md5_chunksize", "'big'", "An integer is required: 'big'"),
    ("hash_chunksize", "'small'", "An integer is required: 'small'"),
)

for opt, value, expect in badopts:
    SConstruct = "SC-" + opt
    test.write(
        SConstruct,
        """\
DefaultEnvironment(tools=[])
SetOption("%(opt)s", %(value)s)
"""
        % locals(),
    )
    expect = r"scons: *** %s" % expect
    test.run(arguments='-Q -f %s .' % SConstruct, stderr=None, status=2)
    test.must_contain_all(test.stderr(), expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
