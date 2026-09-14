#!/usr/bin/env python
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
#

"""
Test that a DocBook source pulling in an external entity module builds.

lxml 6.1.3 stopped resolving external parameter entities by default
(https://bugs.launchpad.net/lxml/+bug/2165901), which broke any document
using the

    <!ENTITY % myents SYSTEM "entities.mod">
    %myents;

idiom until the docbook tool started asking for entity resolution explicitly.
"""

import TestSCons

test = TestSCons.TestSCons()

try:
    import lxml # noqa: F401
except Exception:
    test.skip_test('Cannot find installed Python binding for lxml, skipping test.\n')

test.dir_fixture('image')

# Normal invocation
test.run()
test.must_not_be_empty(test.workpath('manual_xi.xml'))
test.must_contain(
    test.workpath('manual_xi.xml'),
    'This is text from an external entity module.',
    mode='r',
)

# Cleanup
test.run(arguments='-c')
test.must_not_exist(test.workpath('manual_xi.xml'))

test.pass_test()
