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


if not test.where_is('msgmerge'):
    test.skip_test("Could not find 'msgmerge'; skipping test(s)\n")

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

en_po_contents = """\
# English translations for PACKAGE package.
# Copyright (C) 2012 THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# Pawel Tomulik <ptomulik@meil.pw.edu.pl>, 2012.
#
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2012-05-27 00:35+0200\\n"
"PO-Revision-Date: 2012-05-27 00:37+0200\\n"
"Last-Translator: Pawel Tomulik <ptomulik@meil.pw.edu.pl>\\n"
"Language-Team: English\\n"
"Language: en\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=ASCII\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"

#: a.cpp:1
msgid "Old message from a.cpp"
msgstr "Old message from a.cpp"
"""

pl_po_contents = """\
# Polish translations for PACKAGE package.
# Copyright (C) 2012 THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# Automatically generated, 2012.
#
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2012-05-27 00:35+0200\\n"
"PO-Revision-Date: 2012-05-27 00:35+0200\\n"
"Last-Translator: Automatically generated\\n"
"Language-Team: none\\n"
"Language: pl\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=ASCII\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=3; plural=(n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 "
"|| n%100>=20) ? 1 : 2);\\n"

#: a.cpp:1
msgid "Old message from a.cpp"
msgstr "Stara wiadomosc z a.cpp"
"""

de_po_contents = """\
# German translations for PACKAGE package.
# Copyright (C) 2012 THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# Automatically generated, 2012.
#
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2012-05-27 00:35+0200\\n"
"PO-Revision-Date: 2012-05-27 00:35+0200\\n"
"Last-Translator: Automatically generated\\n"
"Language-Team: none\\n"
"Language: de\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=ASCII\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"

#: a.cpp:1
msgid "Old message from a.cpp"
msgstr "EINE ALTE Nachricht vom a.cpp"
"""

fr_po_contents = """\
# French translations for PACKAGE package.
# Copyright (C) 2012 THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# Automatically generated, 2012.
#
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2012-05-27 00:35+0200\\n"
"PO-Revision-Date: 2012-05-27 00:35+0200\\n"
"Last-Translator: Automatically generated\\n"
"Language-Team: none\\n"
"Language: fr\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=ASCII\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=2; plural=(n > 1);\\n"

#: a.cpp:1
msgid "Old message from a.cpp"
msgstr "Un ancien message du a.cpp"
"""

#############################################################################
# POUpdate: Example 1
#############################################################################
test.subdir(['ex1'])
test.write( ['ex1', 'SConstruct'],
"""
env = Environment( tools = ["default", "msgmerge"] )
env.POUpdate(['en','pl']) # messages.pot --&gt; [en.po, pl.po]
""")
test.write(['ex1', 'messages.pot'], pot_contents)
test.write(['ex1', 'en.po'], en_po_contents)
test.write(['ex1', 'pl.po'], pl_po_contents)

# NOTE: msgmerge(1) prints its messages to stderr, we must ignore them,
# So, stderr=None is crucial here. It is no point to match stderr to some
# specific valuse; the messages are internationalized :) ).
test.run(arguments = 'po-update', chdir = 'ex1', stderr = None)
test.must_exist(    ['ex1', 'en.po'] )
test.must_exist(    ['ex1', 'pl.po'] )
test.must_contain(  ['ex1', 'en.po'], "Hello from a.cpp", mode='r' )
test.must_contain(  ['ex1', 'pl.po'], "Hello from a.cpp", mode='r' )

#############################################################################
# POUpdate: Example 2
#############################################################################
test.subdir(['ex2'])
test.write( ['ex2', 'SConstruct'],
"""
env = Environment( tools = ["default", "msgmerge"] )
env.POUpdate(['en','pl'], ['foo']) # foo.pot --&gt; [en.po, pl.po]
""")
#
test.write(['ex2', 'foo.pot'], pot_contents)
test.write(['ex2', 'en.po'], en_po_contents)
test.write(['ex2', 'pl.po'], pl_po_contents)

# NOTE: msgmerge(1) prints all messages to stderr, we must ignore them,
# So, stderr=None is crucial here. It is no point to match stderr to some
# specific valuse; the messages are internationalized :) ).
test.run(arguments = 'po-update', chdir = 'ex2', stderr = None)
test.must_exist(    ['ex2', 'en.po'] )
test.must_exist(    ['ex2', 'pl.po'] )
test.must_contain(  ['ex2', 'en.po'], "Hello from a.cpp", mode='r' )
test.must_contain(  ['ex2', 'pl.po'], "Hello from a.cpp", mode='r' )

#############################################################################
# POUpdate: Example 3
#############################################################################
test.subdir(['ex3'])
test.write( ['ex3', 'SConstruct'],
"""
env = Environment( tools = ["default", "msgmerge"] )
env.POUpdate(['en','pl'], POTDOMAIN='foo') # foo.pot --&gt; [en.po, pl.po]
""")
#
test.write(['ex3', 'foo.pot'], pot_contents)
test.write(['ex3', 'en.po'], en_po_contents)
test.write(['ex3', 'pl.po'], pl_po_contents)

# NOTE: msgmerge(1) prints its messages to stderr, we must ignore them,
# So, stderr=None is crucial here. It is no point to match stderr to some
# specific valuse; the messages are internationalized :) ).
test.run(arguments = 'po-update', chdir = 'ex3', stderr = None)
test.must_exist(    ['ex3', 'en.po'] )
test.must_exist(    ['ex3', 'pl.po'] )
test.must_contain(  ['ex3', 'en.po'], "Hello from a.cpp", mode='r' )
test.must_contain(  ['ex3', 'pl.po'], "Hello from a.cpp", mode='r' )

#############################################################################
# POUpdate: Example 4
#############################################################################
test.subdir(['ex4'])
test.write( ['ex4', 'SConstruct'],
"""
env = Environment( tools = ["default", "msgmerge"] )
env.POUpdate(LINGUAS_FILE = 1) # needs 'LINGUAS' file
""")
#
test.write(['ex4', 'LINGUAS'],
"""
en
pl
""")
#
test.write(['ex4', 'messages.pot'], pot_contents)
test.write(['ex4', 'en.po'], en_po_contents)
test.write(['ex4', 'pl.po'], pl_po_contents)

# NOTE: msgmerge(1) prints all messages to stderr, we must ignore them,
# So, stderr=None is crucial here. It is no point to match stderr to some
# specific valuse; the messages are internationalized :) ).
test.run(arguments = 'po-update', chdir = 'ex4', stderr = None)
test.must_exist(    ['ex4', 'messages.pot'] )
test.must_exist(    ['ex4', 'en.po'] )
test.must_exist(    ['ex4', 'pl.po'] )
test.must_contain(  ['ex4', 'en.po'], "Hello from a.cpp", mode='r' )
test.must_contain(  ['ex4', 'pl.po'], "Hello from a.cpp", mode='r' )

#############################################################################
# POUpdate: Example 5
#############################################################################
test.subdir(['ex5'])
test.write( ['ex5', 'SConstruct'],
"""
env = Environment( tools = ["default", "msgmerge"] )
env.POUpdate(LINGUAS_FILE = 1, source = ['foo']) 
""")
test.write(['ex5', 'LINGUAS'],
"""
en
pl
""")
#
test.write(['ex5', 'foo.pot'], pot_contents)
test.write(['ex5', 'en.po'], en_po_contents)
test.write(['ex5', 'pl.po'], pl_po_contents)

# NOTE: msgmerge(1) prints its messages to stderr, we must ignore them,
# So, stderr=None is crucial here. It is no point to match stderr to some
# specific valuse; the messages are internationalized :) ).
test.run(arguments = 'po-update', chdir=  'ex5', stderr = None)
test.must_exist(    ['ex5', 'en.po'] )
test.must_exist(    ['ex5', 'pl.po'] )
test.must_contain(  ['ex5', 'en.po'], "Hello from a.cpp", mode='r' )
test.must_contain(  ['ex5', 'pl.po'], "Hello from a.cpp", mode='r' )

#############################################################################
# POUpdate: Example 6
#############################################################################
test.subdir(['ex6'])
test.write( ['ex6', 'SConstruct'],
"""
env = Environment( tools = ["default", "msgmerge"] )
env.POUpdate(['en', 'pl'], LINGUAS_FILE = 1)
""")
test.write(['ex6', 'LINGUAS'],
"""
de
fr
""")
test.write(['ex6', 'messages.pot'], pot_contents)
test.write(['ex6', 'en.po'], en_po_contents)
test.write(['ex6', 'pl.po'], pl_po_contents)
test.write(['ex6', 'de.po'], de_po_contents)
test.write(['ex6', 'fr.po'], fr_po_contents)

# Note: msgmerge(1) prints its messages to stderr, we must ignore them,
# So, stderr=None is crucial here. It is no point to match stderr to some
# specific valuse; the messages are internationalized :) ).
test.run(arguments = 'po-update', chdir = 'ex6', stderr = None)
test.must_exist(    ['ex6', 'en.po'] )
test.must_exist(    ['ex6', 'pl.po'] )
test.must_exist(    ['ex6', 'de.po'] )
test.must_exist(    ['ex6', 'fr.po'] )
test.must_contain(  ['ex6', 'en.po'], "Hello from a.cpp", mode='r' )
test.must_contain(  ['ex6', 'pl.po'], "Hello from a.cpp", mode='r' )
test.must_contain(  ['ex6', 'de.po'], "Hello from a.cpp", mode='r' )
test.must_contain(  ['ex6', 'fr.po'], "Hello from a.cpp", mode='r' )

#############################################################################
# POUpdate: Example 7
#############################################################################
#
# From this poin we need msginit
#
if not test.where_is('msginit'):
    test.skip_test("could not find 'msginit'; skipping test(s)\n")
###
test.subdir(['ex7'])
test.write( ['ex7', 'SConstruct'],
"""
env = Environment( tools = ["default", "msginit", "msgmerge"] )
env.POUpdate(LINGUAS_FILE = 1, POAUTOINIT = 1) 
""")
test.write(['ex7', 'LINGUAS'],
"""
en
pl
""")
#
test.write(['ex7', 'messages.pot'], pot_contents)

# NOTE: msgmerge(1) prints its messages to stderr, we must ignore them,
# So, stderr=None is crucial here. It is no point to match stderr to some
# specific valuse; the messages are internationalized :) ).
test.run(arguments = 'po-update', chdir=  'ex7', stderr = None)
test.must_exist(    ['ex7', 'en.po'] )
test.must_exist(    ['ex7', 'pl.po'] )
test.must_contain(  ['ex7', 'en.po'], "Hello from a.cpp", mode='r' )
test.must_contain(  ['ex7', 'pl.po'], "Hello from a.cpp", mode='r' )

#############################################################################
# POUpdate: Example 8
#############################################################################
#
# From this point we need xgettext
#
if not test.where_is('xgettext'):
    test.skip_test("could not find 'xgettext'; skipping test(s)\n")
###
test.subdir(['ex8'])
test.write( ['ex8', 'SConstruct'],
"""
env = Environment( tools = ["default", "xgettext", "msginit", "msgmerge"] )

# script-wise settings
env['POAUTOINIT'] = 1
env['LINGUAS_FILE'] = 1
env['POTDOMAIN'] = 'foo'
env.POTUpdate(source = 'a.cpp')
env.POUpdate()
""")
test.write(['ex8', 'LINGUAS'],
"""
en
pl
""")
test.write(['ex8', 'a.cpp'], """ gettext("Hello from a.cpp") """)

# Note: msgmerge(1) prints its messages to stderr, we must ignore them,
# So, stderr=None is crucial here. It is no point to match stderr to some
# specific valuse; the messages are internationalized :) ).
test.run(arguments = 'po-update', chdir = 'ex8', stderr = None)
test.must_exist(    ['ex8', 'foo.pot'] )
test.must_exist(    ['ex8', 'en.po'] )
test.must_exist(    ['ex8', 'pl.po'] )
test.must_contain(  ['ex8', 'en.po'], "Hello from a.cpp", mode='r' )
test.must_contain(  ['ex8', 'pl.po'], "Hello from a.cpp", mode='r' )

test.pass_test()


# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
