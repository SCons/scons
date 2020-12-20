
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

if not test.where_is('msgfmt'):
    test.skip_test("Could not find 'msgfmt'; skipping test(s)\n")

en_po_contents = """\
# English translations for PACKAGE package.
# Copyright (C) 2012 THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# Pawel Tomulik <ptomulik@meil.pw.edu.pl>, 2012.
#
msgid ""
msgstr ""
"Project-Id-Version: dummypkg 1.0\\n"
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
"Project-Id-Version: dummypkg 1.0\\n"
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
"Project-Id-Version: dummypkg 1.0\\n"
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
msgstr ""
"""

fr_po_contents = """\
# French translations for PACKAGE package.
# Copyright (C) 2012 THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# Automatically generated, 2012.
#
msgid ""
msgstr ""
"Project-Id-Version: dummypkg 1.0\\n"
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
msgstr ""
"""

#############################################################################
# MOFiles: Example 1
#############################################################################
test.subdir(['ex1'])
test.write( ['ex1', 'SConstruct'],
"""
env = Environment( tools = ["default", "msgfmt"] )
env.MOFiles(['pl', 'en'])
""")
test.write(['ex1', 'en.po'], en_po_contents)
test.write(['ex1', 'pl.po'], pl_po_contents)

test.run(arguments = '.', chdir = 'ex1')
test.must_exist(['ex1', 'en.mo'])
test.must_exist(['ex1', 'pl.mo'])


#############################################################################
# MOFiles: Example 2
#############################################################################
test.subdir(['ex2'])
test.write( ['ex2', 'SConstruct'],
"""
env = Environment( tools = ["default", "msgfmt"] )
env.MOFiles(LINGUAS_FILE = 1)
""")
#
test.write(['ex2', 'LINGUAS'],
"""
en
pl
""")
#
test.write(['ex2', 'en.po'], en_po_contents)
test.write(['ex2', 'pl.po'], pl_po_contents)

test.run(arguments = '.', chdir = 'ex2')
test.must_exist(['ex2', 'en.mo'])
test.must_exist(['ex2', 'pl.mo'])


#############################################################################
# MOFiles: Example 3
#############################################################################
test.subdir(['ex3'])
test.write( ['ex3', 'SConstruct'],
"""
env = Environment( tools = ["default", "msgfmt"] )
env.MOFiles(['en', 'pl'], LINGUAS_FILE = 1)
""")
test.write(['ex3', 'LINGUAS'],
"""
de
fr
""")
#
test.write(['ex3', 'en.po'], en_po_contents)
test.write(['ex3', 'pl.po'], pl_po_contents)
test.write(['ex3', 'de.po'], de_po_contents)
test.write(['ex3', 'fr.po'], fr_po_contents)

test.run(arguments = '.', chdir = 'ex3')
test.must_exist(['ex3', 'en.mo'])
test.must_exist(['ex3', 'pl.mo'])
test.must_exist(['ex3', 'de.mo'])
test.must_exist(['ex3', 'fr.mo'])


#############################################################################
# MOFiles: Example 4
#############################################################################
test.subdir(['ex4'])
test.write( ['ex4', 'SConstruct'],
"""
env = Environment( tools = ["default", "msgfmt"] )
env['LINGUAS_FILE'] = 1
env.MOFiles()
""")

test.write(['ex4', 'LINGUAS'],
"""
en
pl
""")

test.write(['ex4', 'en.po'], en_po_contents)
test.write(['ex4', 'pl.po'], pl_po_contents)

test.run(arguments = '.', chdir = 'ex4')
test.must_exist(['ex4', 'en.mo'])
test.must_exist(['ex4', 'pl.mo'])

test.pass_test()


# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
