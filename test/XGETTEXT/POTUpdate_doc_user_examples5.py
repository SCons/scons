
#!/usr/bin/env python
#
# __TOOL_COPYRIGHT__
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

"""
Make sure, that the examples given in user guide all work.
"""

import TestSCons
import os

site_scons =  os.environ['SCONS_TOOL_LIB_DIR'] 

###############################################################################
test = TestSCons.TestSCons()

test.subdir('0', ['0','1'], ['0', '1', 'po'])
test.write('0/1/po/SConstruct',
"""
# SConstruct file in '0/1/po/' subdirectory
env = Environment( tools = ['default', 'xgettext'] )
env.POTUpdate(XGETTEXTFROM = 'POTFILES.in', XGETTEXTPATH=['../', '../../'])
""")
test.write('0/1/po/POTFILES.in',
"""
# POTFILES.in in '0/1/po/' subdirectory
a.cpp
# end of file
""")
test.write('0/a.cpp', """ gettext("Hello from ../../a.cpp") """)
test.write('0/1/a.cpp', """ gettext("Hello from ../a.cpp") """)

# scons 'pot-update' creates messages.pot
test.run(arguments = 'pot-update', chdir = '0/1/po')
test.must_exist('0/1/po/messages.pot')
test.must_contain('0/1/po/messages.pot', 'Hello from ../a.cpp')
test.must_not_contain('0/1/po/messages.pot', 'Hello from ../../a.cpp')

test.write('0/1/po/SConstruct',
"""
# SConstruct file in '0/1/po/' subdirectory
env = Environment(
  toolpath = ['""" + site_scons + """/SConsToolGettext']
, tools = ['default', 'xgettext']
)
env.POTUpdate(XGETTEXTFROM = 'POTFILES.in', XGETTEXTPATH=['../../', '../'])
""")
test.run(arguments = 'pot-update', chdir = '0/1/po')
test.must_contain('0/1/po/messages.pot', 'Hello from ../../a.cpp')
test.must_not_contain('0/1/po/messages.pot', 'Hello from ../a.cpp')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
