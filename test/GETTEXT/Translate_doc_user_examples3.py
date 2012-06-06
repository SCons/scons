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

# NOTE: When integrating into upstream SCons development tree, remove the next
#       line, and the "toolpath = ..." line 
site_scons =  os.environ['SCONS_TOOL_LIB_DIR'] 

###############################################################################
# Trivial example. Just load the tool.
test = TestSCons.TestSCons()

test.subdir('src', ['src', 'po'], 'build')
test.write('SConstruct',
"""
env = Environment(
  toolpath = ['""" + site_scons + """/SConsToolGettext']
, tools = ["default", "gettext"]
)
VariantDir('build', 'src', duplicate = 0)
env['POAUTOINIT'] = 1
SConscript('src/po/SConscript.i18n', exports = 'env')
SConscript('build/po/SConscript', exports = 'env')
""")
#
test.write('src/po/SConscript.i18n', """\
# src/po/SConscript.i18n
Import('env')
env.Translate(LINGUAS_FILE=1, XGETTEXTFROM='POTFILES.in', XGETTEXTPATH=['../'])
""")
#
test.write('src/po/SConscript',"""\
# src/po/SConscript
Import('env')
env.MOFiles(LINGUAS_FILE = 1)
""")
test.write('src/po/LINGUAS', """\
en pl
""")
#
test.write('src/po/POTFILES.in', """\
# POTFILES.in
a.cpp
b.cpp
# end
""")
#
test.write('src/a.cpp', """ gettext("Hello from a.cpp") """)
test.write('src/b.cpp', """ gettext("Hello from b.cpp") """)

# NOTE: msginit(1) prints all its messages to stderr, we must ignore them,
# So, stderr=None is crucial here. It is no point to match stderr to some
# specific valuse; the messages are internationalized :) ).
test.run(arguments = 'po-update', stderr = None)
test.must_exist('src/po/messages.pot')
test.must_exist('src/po/en.po', 'src/po/pl.po')
test.must_not_exist('build/po/en.po', 'build/po/pl.po')
test.must_contain('src/po/en.po', "Hello from a.cpp")
test.must_contain('src/po/en.po', "Hello from b.cpp")
test.must_contain('src/po/pl.po', "Hello from a.cpp")
test.must_contain('src/po/pl.po', "Hello from b.cpp")

test.run(arguments = '.', stderr = None)
test.must_exist('build/po/en.mo', 'build/po/pl.mo')
test.must_not_exist('src/po/en.mo', 'src/po/pl.mo')

test.run(arguments = '-c', stderr = None)
test.must_exist('src/po/messages.pot')
test.must_exist('src/po/en.po', 'src/po/pl.po')
test.must_not_exist('build/po/en.mo', 'build/po/pl.mo')

test.pass_test()


# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
