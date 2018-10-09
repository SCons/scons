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
Validate that a stripped-down real-world Qt configuation (thanks
to Leanid Nazdrynau) with a generated .h file is correctly
up-to-date after a build.

(This catches a bug that was introduced during a signature refactoring
ca. September 2005.)
"""

import os

import TestSCons

_obj = TestSCons._obj

test = TestSCons.TestSCons()

if not os.environ.get('QTDIR', None):
    x ="External environment variable $QTDIR not set; skipping test(s).\n"
    test.skip_test(x)

test.subdir('layer',
            ['layer', 'aclock'],
            ['layer', 'aclock', 'qt_bug'])

test.write('SConstruct', """\
import os
aa=os.getcwd()

env=Environment(tools=['default','expheaders','qt'],toolpath=[aa])
env["EXP_HEADER_ABS"]=os.path.join(os.getcwd(),'include')
if not os.access(env["EXP_HEADER_ABS"],os.F_OK):
   os.mkdir (env["EXP_HEADER_ABS"])
Export('env')
env.SConscript('layer/aclock/qt_bug/SConscript')
""")

test.write('expheaders.py', """\
import SCons.Defaults
def ExpHeaderScanner(node, env, path):
   return []
def generate(env):
   HeaderAction=SCons.Action.Action([SCons.Defaults.Copy('$TARGET','$SOURCE'),SCons.Defaults.Chmod('$TARGET',0o755)])
   HeaderBuilder= SCons.Builder.Builder(action=HeaderAction)
   env['BUILDERS']['ExportHeaders'] = HeaderBuilder
def exists(env):
   return 0
""")

test.write(['layer', 'aclock', 'qt_bug', 'SConscript'], """\
import os

Import ("env")
env.ExportHeaders(os.path.join(env["EXP_HEADER_ABS"],'main.h'), 'main.h')
env.ExportHeaders(os.path.join(env["EXP_HEADER_ABS"],'migraform.h'), 'migraform.h')
env.Append(CPPPATH=env["EXP_HEADER_ABS"])
env.StaticLibrary('all',['main.ui','migraform.ui','my.cc'])
""")

test.write(['layer', 'aclock', 'qt_bug', 'main.ui'], """\
<!DOCTYPE UI><UI version="3.3" stdsetdef="1">
<class>Main</class>
<widget class="QWizard">
    <property name="name">
        <cstring>Main</cstring>
    </property>
    <property name="geometry">
        <rect>
            <x>0</x>
            <y>0</y>
            <width>600</width>
            <height>385</height>
        </rect>
    </property>
</widget>
<includes>
    <include location="local" impldecl="in implementation">migraform.h</include>
</includes>
</UI>
""")

test.write(['layer', 'aclock', 'qt_bug', 'migraform.ui'], """\
<!DOCTYPE UI><UI version="3.3" stdsetdef="1">
<class>MigrateForm</class>
<widget class="QWizard">
    <property name="name">
        <cstring>MigrateForm</cstring>
    </property>
    <property name="geometry">
        <rect>
            <x>0</x>
            <y>0</y>
            <width>600</width>
            <height>385</height>
        </rect>
    </property>
</widget>
</UI>
""")

test.write(['layer', 'aclock', 'qt_bug', 'my.cc'], """\
#include <main.h>
""")

my_obj = 'layer/aclock/qt_bug/my'+_obj

test.run(arguments = my_obj, stderr=None)

expect = my_obj.replace( '/', os.sep )
test.up_to_date(options = '--debug=explain',
                arguments = (expect),
                stderr=None)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
