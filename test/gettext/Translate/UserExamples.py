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

"""
Ensure that examples given in user guide work.
"""

import TestSCons
from os import path

test = TestSCons.TestSCons()

if not test.where_is('xgettext'):
    test.skip_test("could not find 'xgettext'; skipping test(s)\n")
if not test.where_is('msgmerge'):
    test.skip_test("Could not find 'msgmerge'; skipping test(s)\n")
if not test.where_is('msginit'):
    test.skip_test("could not find 'msginit'; skipping test(s)\n")
if not test.where_is('msgfmt'):
    # We really don't use it until the Example 3, but we load "gettext" tool,
    # which depends on msgfmt.
    test.skip_test("could not find 'msgfmt'; skipping test(s)\n")


#############################################################################
# Translate: Example 1
#############################################################################
test.subdir(['ex1'])
test.subdir(['ex1', 'po'])
test.write( ['ex1', 'po', 'SConstruct'],
"""
env = Environment( tools = ["default", "gettext"] )
env['POAUTOINIT'] = 1
env.Translate(['en','pl'], ['../a.cpp', '../b.cpp'])
""")
test.write(['ex1', 'a.cpp'], """ gettext("Hello from a.cpp") """ )
test.write(['ex1', 'b.cpp'], """ gettext("Hello from b.cpp") """)

# NOTE: msgmerge(1) prints its messages to stderr, we must ignore them,
# So, stderr=None is crucial here. It is no point to match stderr to some
# specific valuse; the messages are internationalized :) ).
test.run(arguments = 'po-update', chdir = path.join('ex1','po'), stderr = None)
test.must_exist(    ['ex1', 'po', 'en.po'] )
test.must_exist(    ['ex1', 'po', 'pl.po'] )
test.must_contain(  ['ex1', 'po', 'en.po'], "Hello from a.cpp", mode='r' )
test.must_contain(  ['ex1', 'po', 'en.po'], "Hello from b.cpp", mode='r' )
test.must_contain(  ['ex1', 'po', 'pl.po'], "Hello from a.cpp", mode='r' )
test.must_contain(  ['ex1', 'po', 'pl.po'], "Hello from b.cpp", mode='r' )

#############################################################################
# Translate: Example 2
#############################################################################
test.subdir(['ex2'])
test.subdir(['ex2', 'po'])
test.write( ['ex2', 'po', 'SConstruct'],
"""
env = Environment( tools = ["default", "gettext"] )
env['POAUTOINIT'] = 1
env['XGETTEXTPATH'] = ['../']
env.Translate(LINGUAS_FILE = 1, XGETTEXTFROM = 'POTFILES.in')
""")
test.write(['ex2', 'po', 'LINGUAS'], """
# LINGUAS
en pl
#end""")
test.write(['ex2', 'po', 'POTFILES.in'], """
# POTFILES.in
a.cpp
b.cpp
# end""")
test.write(['ex2', 'a.cpp'], """ gettext("Hello from a.cpp") """ )
test.write(['ex2', 'b.cpp'], """ gettext("Hello from b.cpp") """)

# NOTE: msgmerge(1) prints its messages to stderr, we must ignore them,
# So, stderr=None is crucial here. It is no point to match stderr to some
# specific valuse; the messages are internationalized :) ).
test.run(arguments = 'po-update', chdir = path.join('ex2','po'), stderr = None)
test.must_exist(    ['ex2', 'po', 'en.po'] )
test.must_exist(    ['ex2', 'po', 'pl.po'] )
test.must_contain(  ['ex2', 'po', 'en.po'], "Hello from a.cpp", mode='r' )
test.must_contain(  ['ex2', 'po', 'en.po'], "Hello from b.cpp", mode='r' )
test.must_contain(  ['ex2', 'po', 'pl.po'], "Hello from a.cpp", mode='r' )
test.must_contain(  ['ex2', 'po', 'pl.po'], "Hello from b.cpp", mode='r' )

#############################################################################
# Translate: Example 3
#############################################################################
test.subdir(['ex3'])
test.subdir(['ex3', 'build'])
test.subdir(['ex3', 'src'])
test.subdir(['ex3', 'src', 'po'])
test.write( ['ex3', 'Sconstruct'],
"""
# SConstruct
env = Environment( tools = ["default", "gettext"] )
VariantDir('build', 'src', duplicate = 0)
env['POAUTOINIT'] = 1
SConscript('src/po/SConscript.i18n', exports = 'env')
SConscript('build/po/SConscript', exports = 'env')
""")
test.write( ['ex3', 'src', 'po', 'SConscript.i18n'],
"""
# src/po/SConscript.i18n
Import('env')
env.Translate(LINGUAS_FILE=1, XGETTEXTFROM='POTFILES.in', XGETTEXTPATH=['../'])
""")
test.write( ['ex3', 'src', 'po', 'SConscript'],
"""
# src/po/SConscript
Import('env')
env.MOFiles(LINGUAS_FILE = 1)
""")
test.write(['ex3', 'src', 'po', 'LINGUAS'], """
# LINGUAS
en pl
#end""")
test.write(['ex3', 'src', 'po', 'POTFILES.in'], """
# POTFILES.in
a.cpp
b.cpp
# end""")
test.write(['ex3', 'src', 'a.cpp'], """ gettext("Hello from a.cpp") """ )
test.write(['ex3', 'src', 'b.cpp'], """ gettext("Hello from b.cpp") """)

# NOTE: msgmerge(1) prints its messages to stderr, we must ignore them,
# So, stderr=None is crucial here. It is no point to match stderr to some
# specific valuse; the messages are internationalized :) ).
test.run(arguments = 'po-update', chdir = 'ex3', stderr = None)
test.must_exist(        ['ex3', 'src', 'po', 'messages.pot'] )
test.must_exist(        ['ex3', 'src', 'po', 'en.po'] )
test.must_exist(        ['ex3', 'src', 'po', 'pl.po'] )
#
test.must_not_exist(    ['ex3', 'build', 'po', 'messages.pot'] )
test.must_not_exist(    ['ex3', 'build', 'po', 'en.po'] )
test.must_not_exist(    ['ex3', 'build', 'po', 'pl.po'] )
#
test.must_contain(  ['ex3', 'src', 'po', 'messages.pot'], "Hello from a.cpp", mode='r' )
test.must_contain(  ['ex3', 'src', 'po', 'messages.pot'], "Hello from b.cpp", mode='r' )
test.must_contain(  ['ex3', 'src', 'po', 'en.po'], "Hello from a.cpp", mode='r' )
test.must_contain(  ['ex3', 'src', 'po', 'en.po'], "Hello from b.cpp", mode='r' )
test.must_contain(  ['ex3', 'src', 'po', 'pl.po'], "Hello from a.cpp", mode='r' )
test.must_contain(  ['ex3', 'src', 'po', 'pl.po'], "Hello from b.cpp", mode='r' )

test.run(arguments = '.', chdir = 'ex3', stderr = None)
test.must_exist(        ['ex3', 'build', 'po', 'en.mo'] )
test.must_exist(        ['ex3', 'build', 'po', 'pl.mo'] )
test.must_not_exist(    ['ex3', 'src', 'po', 'en.mo'] )
test.must_not_exist(    ['ex3', 'src', 'po', 'pl.mo'] )

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
