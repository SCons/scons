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
Verify that the $IMPLICIT_COMMAND_DEPENDENCIES variable controls
whether or not the implicit dependency on executed commands
is added to targets.
"""

import TestSCons

# swap slashes because on py3 on win32 inside the generated build.py 
# the backslashes are getting interpretted as unicode which is
# invalid.
python = TestSCons.python.replace('\\','//')
_python_ = TestSCons._python_

test = TestSCons.TestSCons()

generate_build_py_py_contents = """\
#!%(python)s
import os
import sys

with open(sys.argv[1], 'w') as f:
    f.write('''\
#!/usr/bin/env %(python)s
import os
import sys
with open(sys.argv[1], 'w') as fp:
    args = [os.path.split(sys.argv[0])[1]] + sys.argv[1:]
    fp.write(" ".join(args) + '\\\\n' + '%(extra)s')
    for infile in sys.argv[2:]:
        with open(infile, 'r') as ifp:
            fp.write(ifp.read())
''')
os.chmod(sys.argv[1], 0o755)

"""

extra = ''
test.write('generate_build_py.py', generate_build_py_py_contents % locals())

test.write('SConstruct', """
DefaultEnvironment(tools=[])
generate = Builder(action = r'%(_python_)s $GENERATE $TARGET')
build = Builder(action = r'$BUILD_PY $TARGET $SOURCES')
env = Environment(tools=[],
                  BUILDERS = {
                        'GenerateBuild' : generate,
                        'BuildFile' : build,
                  },
                  GENERATE = 'generate_build_py.py',
                  BUILD_PY = 'build.py',
                  )
env.PrependENVPath('PATH', '.')
env.PrependENVPath('PATHEXT', '.PY')
env0        = env.Clone(IMPLICIT_COMMAND_DEPENDENCIES = 0)
env1        = env.Clone(IMPLICIT_COMMAND_DEPENDENCIES = 1)
envNone     = env.Clone(IMPLICIT_COMMAND_DEPENDENCIES = None)
envFalse    = env.Clone(IMPLICIT_COMMAND_DEPENDENCIES = False)
envTrue     = env.Clone(IMPLICIT_COMMAND_DEPENDENCIES = True)

build_py = env.GenerateBuild('${BUILD_PY}', [])
AlwaysBuild(build_py)

env.BuildFile('file.out',               'file.in')
env0.BuildFile('file0.out',             'file.in')
env1.BuildFile('file1.out',             'file.in')
envNone.BuildFile('fileNone.out',       'file.in')
envFalse.BuildFile('fileFalse.out',     'file.in')
envTrue.BuildFile('fileTrue.out',       'file.in')
envTrue.BuildFile('fileQuote.out',      'file.in', BUILD_PY='"build.py"')
""" % locals())



test.write('file.in',     "file.in\n")

test.run(arguments = '--tree=all .')

expect_none = 'build.py %s file.in\nfile.in\n'

test.must_match('file.out',         expect_none % 'file.out', mode='r')
test.must_match('file0.out',        expect_none % 'file0.out', mode='r')
test.must_match('file1.out',        expect_none % 'file1.out', mode='r')
test.must_match('fileNone.out',     expect_none % 'fileNone.out', mode='r')
test.must_match('fileFalse.out',    expect_none % 'fileFalse.out', mode='r')
test.must_match('fileTrue.out',     expect_none % 'fileTrue.out', mode='r')
test.must_match('fileQuote.out',    expect_none % 'fileQuote.out', mode='r')



extra = 'xyzzy\\\\n'
test.write('generate_build_py.py', generate_build_py_py_contents % locals())

test.run(arguments = '--tree=all .')

expect_extra = 'build.py %s file.in\nxyzzy\nfile.in\n'

test.must_match('file.out',         expect_extra % 'file.out', mode='r')
test.must_match('file0.out',        expect_none % 'file0.out', mode='r')
test.must_match('file1.out',        expect_extra % 'file1.out', mode='r')
test.must_match('fileNone.out',     expect_none % 'fileNone.out', mode='r')
test.must_match('fileFalse.out',    expect_none % 'fileFalse.out', mode='r')
test.must_match('fileTrue.out',     expect_extra % 'fileTrue.out', mode='r')
test.must_match('fileQuote.out',    expect_extra % 'fileQuote.out', mode='r')


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
