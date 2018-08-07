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
Test that the UI scanning logic correctly picks up scansG
"""

import os

import TestSCons

test = TestSCons.TestSCons()

if not os.environ.get('QTDIR', None):
    x ="External environment variable $QTDIR not set; skipping test(s).\n"
    test.skip_test(x)

test.subdir(['layer'],
            ['layer', 'aclock'],
            ['layer', 'aclock', 'qt_bug'])

test.write(['SConstruct'], """\
import os
aa=os.getcwd()

env=Environment(tools=['default','expheaders','qt'],toolpath=[aa])
if 'HOME' in os.environ:
    env['ENV']['HOME'] = os.environ['HOME']
env["EXP_HEADER_ABS"]=os.path.join(os.getcwd(),'include')
if not os.access(env["EXP_HEADER_ABS"],os.F_OK):
   os.mkdir (env["EXP_HEADER_ABS"])
Export('env')
env.SConscript('layer/aclock/qt_bug/SConscript')
""")

test.write(['expheaders.py'], """\
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
#src=os.path.join(env.Dir('.').srcnode().abspath, 'testfile.h')
env.ExportHeaders(os.path.join(env["EXP_HEADER_ABS"],'main.h'), 'main.h')
env.ExportHeaders(os.path.join(env["EXP_HEADER_ABS"],'migraform.h'), 'migraform.h')
env.Append(CPPPATH=env["EXP_HEADER_ABS"])
env.StaticLibrary('all',['main.ui','migraform.ui'])
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
            <width>%s</width>
            <height>385</height>
        </rect>
    </property>
</widget>
</UI>
""")

test.run(arguments = '.',
         stderr = TestSCons.noisy_ar,
         match = TestSCons.match_re_dotall)

test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
