#!/usr/bin/env python
#
# Copyright (c) 2001-2010 The SCons Foundation
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
Test implicit dependencies for the XInclude builder.
"""

import TestSCons

test = TestSCons.TestSCons()

try:
    import libxml2
    import libxslt
except:
    try:
        import lxml
    except:
        test.skip_test('Cannot find installed Python binding for libxml2 or lxml, skipping test.\n')

test.dir_fixture('image')

# Normal invocation
test.run()
test.must_exist(test.workpath('manual_xi.xml'))
test.must_contain(test.workpath('manual_xi.xml'),'<para>This is an included text.', mode='r')

# Change included file
test.write('include.txt', 'This is another text.')

# This should trigger a rebuild
test.not_up_to_date(options='-n', arguments='.')

# The new file should contain the changes
test.run()
test.must_exist(test.workpath('manual_xi.xml'))
test.must_contain(test.workpath('manual_xi.xml'),'<para>This is another text.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
