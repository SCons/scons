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
Make sure, that the examples given in user guide all work.
"""

import TestSCons

test = TestSCons.TestSCons()

if not test.where_is('msginit'):
    test.skip_test("Could not find 'msginit'; skipping test(s)\n")

pot_contents = """\
# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2012-05-27 00:35+0200\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"Language: \\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=CHARSET\\n"
"Content-Transfer-Encoding: 8bit\\n"
#
#: a.cpp:1
msgid "Hello from a.cpp"
msgstr ""
"""

###############################################################################
# POInit: Example 1
###############################################################################
test.subdir(['ex1'])
test.write( ['ex1', 'SConstruct'],
"""
env = Environment( tools = ["default", "msginit"] )
env['POAUTOINIT'] = 1
env.POInit(['en','pl']) # messages.pot --&gt; [en.po, pl.po]
""")
#
test.write(['ex1', 'messages.pot'], pot_contents)

# NOTE: msginit(1) prints all its messages to stderr, we must ignore them,
# So, stderr=None is crucial here. It is no point to match stderr to some
# specific valuse; the messages are internationalized :) ).
test.run(arguments = 'po-create', chdir = 'ex1', stderr = None)
test.must_exist(    ['ex1', 'en.po'] )
test.must_exist(    ['ex1', 'pl.po'] )
test.must_contain(  ['ex1', 'en.po'], "Hello from a.cpp", mode='r')
test.must_contain(  ['ex1', 'pl.po'], "Hello from a.cpp", mode='r')


###############################################################################
# POInit: Example 2
###############################################################################
test.subdir(['ex2'])
test.write( ['ex2', 'SConstruct'],
"""
env = Environment( tools = ["default", "msginit"] )
env['POAUTOINIT'] = 1
env.POInit(['en','pl'], ['foo']) # foo.pot --&gt; [en.po, pl.po]
""")
#
test.write(['ex2', 'foo.pot'], pot_contents)

# NOTE: msginit(1) prints all its messages to stderr, we must ignore them,
# So, stderr=None is crucial here. It is no point to match stderr to some
# specific valuse; the messages are internationalized :) ).
test.run(arguments = 'po-create', chdir = 'ex2', stderr = None)
test.must_exist(    ['ex2', 'en.po'] )
test.must_exist(    ['ex2', 'pl.po'] )
test.must_contain(  ['ex2', 'en.po'], "Hello from a.cpp", mode='r' )
test.must_contain(  ['ex2', 'pl.po'], "Hello from a.cpp", mode='r' )

###############################################################################
# POInit: Example 3
###############################################################################
test.subdir(['ex3'])
test.write( ['ex3', 'SConstruct'],
"""
env = Environment( tools = ["default", "msginit"] )
env['POAUTOINIT'] = 1
env.POInit(['en','pl'], POTDOMAIN='foo') # foo.pot --&gt; [en.po, pl.po]
""")
#
test.write(['ex3', 'foo.pot'], pot_contents)

# NOTE: msginit(1) prints all its messages to stderr, we must ignore them,
# So, stderr=None is crucial here. It is no point to match stderr to some
# specific valuse; the messages are internationalized :) ).
test.run(arguments = 'po-create', chdir = 'ex3', stderr = None)
test.must_exist(    ['ex3', 'en.po'] )
test.must_exist(    ['ex3', 'pl.po'] )
test.must_contain(  ['ex3', 'en.po'], "Hello from a.cpp", mode='r')
test.must_contain(  ['ex3', 'pl.po'], "Hello from a.cpp", mode='r')

###############################################################################
# POInit: Example 4
###############################################################################
test.subdir(['ex4'])
test.write( ['ex4', 'SConstruct'],
"""
env = Environment( tools = ["default", "msginit"] )
env['POAUTOINIT'] = 1
env.POInit(LINGUAS_FILE = 1) # needs 'LINGUAS' file
""")
test.write(['ex4', 'LINGUAS'],"""
en
pl
""")
#
test.write(['ex4', 'messages.pot'], pot_contents)

# NOTE: msginit(1) prints all its messages to stderr, we must ignore them,
# So, stderr=None is crucial here. It is no point to match stderr to some
# specific valuse; the messages are internationalized :) ).
test.run(arguments = 'po-create', chdir = 'ex4', stderr = None)
test.must_exist(    ['ex4', 'en.po'] )
test.must_exist(    ['ex4', 'pl.po'] )
test.must_contain(  ['ex4', 'en.po'], "Hello from a.cpp", mode='r')
test.must_contain(  ['ex4', 'pl.po'], "Hello from a.cpp", mode='r')

###############################################################################
# POInit: Example 5
###############################################################################
test.subdir(['ex5'])
test.write( ['ex5', 'SConstruct'],
"""
env = Environment( tools = ["default", "msginit"] )
env['POAUTOINIT'] = 1
env.POInit(['en', 'pl'], LINGUAS_FILE = 1) # needs 'LINGUAS' file
""")
test.write(['ex5', 'LINGUAS'],"""
de
fr
""")
#
test.write(['ex5', 'messages.pot'], pot_contents)

# NOTE: msginit(1) prints all its messages to stderr, we must ignore them,
# So, stderr=None is crucial here. It is no point to match stderr to some
# specific valuse; the messages are internationalized :) ).
test.run(arguments = 'po-create', chdir = 'ex5', stderr = None)
test.must_exist(    ['ex5', 'en.po'] )
test.must_exist(    ['ex5', 'pl.po'] )
test.must_exist(    ['ex5', 'de.po'] )
test.must_exist(    ['ex5', 'fr.po'] )
test.must_contain(  ['ex5', 'en.po'], "Hello from a.cpp", mode='r')
test.must_contain(  ['ex5', 'pl.po'], "Hello from a.cpp", mode='r')
test.must_contain(  ['ex5', 'de.po'], "Hello from a.cpp", mode='r')
test.must_contain(  ['ex5', 'fr.po'], "Hello from a.cpp", mode='r')

###############################################################################
# POInit: Example 6
###############################################################################
test.subdir(['ex6'])
test.write( ['ex6', 'SConstruct'],
"""
env = Environment( tools = ["default", "msginit"] )
env['POAUTOINIT'] = 1
env['LINGUAS_FILE'] = 1
env['POTDOMAIN'] = 'foo'
env.POInit() 
""")
test.write(['ex6', 'LINGUAS'],"""
en
pl
""")
#
test.write(['ex6', 'foo.pot'], pot_contents)

# NOTE: msginit(1) prints all its messages to stderr, we must ignore them,
# So, stderr=None is crucial here. It is no point to match stderr to some
# specific valuse; the messages are internationalized :) ).
test.run(arguments = 'po-create', chdir = 'ex6', stderr = None)
test.must_exist(    ['ex6', 'en.po'] )
test.must_exist(    ['ex6', 'pl.po'] )
test.must_contain(  ['ex6', 'en.po'], "Hello from a.cpp", mode='r')
test.must_contain(  ['ex6', 'pl.po'], "Hello from a.cpp", mode='r')

test.pass_test()


# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
