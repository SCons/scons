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
Test the XInclude builder.
"""

import TestSCons

test = TestSCons.TestSCons()

test.dir_fixture('image')
test.file_fixture('../../../__init__.py','site_scons/site_tools/docbook/__init__.py')
test.dir_fixture('../../../docbook-xsl-1.76.1','site_scons/site_tools/docbook/docbook-xsl-1.76.1')
test.dir_fixture('../../../utils','site_scons/site_tools/docbook/utils')

# Normal invocation
test.run()
test.must_exist(test.workpath('xincluded_manual.xml'))
test.must_contain(test.workpath('xincluded_manual.xml'),'<para>This is an included text.')


# Cleanup
test.run(arguments='-c')
test.must_not_exist(test.workpath('xincluded_manual.xml'))

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
