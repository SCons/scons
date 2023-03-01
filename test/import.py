#!/usr/bin/env python
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
Verify that we can import and use the contents of Platform and Tool
modules directly.
"""

import os
import re

# must do this here, since TestSCons will chdir
tooldir = os.path.join(os.getcwd(), 'SCons', 'Tool')

import TestSCons
test = TestSCons.TestSCons()

# Before executing any of the platform or tool modules, add some
# null entries to the environment $PATH variable to make sure there's
# no code that tries to index elements from the list before making sure
# they're non-null.
# (This was a problem in checkpoint release 0.97.d020070809.)
os.environ['PATH'] = os.pathsep + os.environ['PATH'] + \
                     os.pathsep + os.pathsep + '/no/such/dir' + os.pathsep

SConstruct_path = test.workpath('SConstruct')

platforms = [
    'aix',
    'cygwin',
    'darwin',
    'hpux',
    'irix',
    'os2',
    'posix',
    'sunos',
    'win32'
]

for platform in platforms:
    test.write('SConstruct', """
DefaultEnvironment(tools=[])
print("Platform %(platform)s")
env = Environment(platform = '%(platform)s', tools=[])
import SCons.Platform.%(platform)s
x = SCons.Platform.%(platform)s.generate
""" % locals())
    test.run()

ignore = ('__init__.py',
        # Can't import these everywhere due to Windows registry dependency.
        '386asm.py', 'linkloc.py',
        # Directory of common stuff for MSVC and MSVS
        'MSCommon',
        # clang common
        "clangCommon",
        # link common logic
        "linkCommon",
        # Sun pkgchk and pkginfo common stuff
        'sun_pkg.py',
        # RPM utilities
        'rpmutils.py',
        )
tools = []
for name in os.listdir(tooldir):
    if name in ignore: continue
    if name[0] == '#': continue
    if name[0:1] == '.': continue
    if name[-1]  == '~' : continue
    if name[-3:] == '.py':
        if name[-8:] not in ('Tests.py', 'ommon.py'):
            tools.append(name[:-3])
    elif os.path.exists(os.path.join(tooldir,name,'__init__.py')):
        tools.append(name)
tools.sort()    # why not?

#if sys.platform == 'win32':
# Just comment out (for now?) due to registry dependency.
#    tools.extend([
#        '386asm',
#        'linkloc',
#    ])

# Intel no compiler warning..
intel_no_compiler_warning = """
scons: warning: Failed to find Intel compiler for version='None', abi='[^']*'
""" + TestSCons.file_expr

# Intel no top dir warning.
intel_no_top_dir_warning = """
scons: warning: Can't find Intel compiler top dir for version='None', abi='[^']*'
""" + TestSCons.file_expr

# Intel no license directory warning
intel_license_warning = re.escape(
r"""scons: warning: Intel license dir was not found.  Tried using the INTEL_LICENSE_FILE environment variable (), the registry () and the default path (C:\Program Files\Common Files\Intel\Licenses).  Using the default path as a last resort.
""") + TestSCons.file_expr

intel_warnings = [
    re.compile(intel_license_warning),
    re.compile(intel_no_compiler_warning),
    re.compile(intel_no_compiler_warning + intel_license_warning),
    re.compile(intel_no_top_dir_warning),
    re.compile(intel_no_top_dir_warning + intel_license_warning),
]

moc = test.where_is('moc')
if moc:
    import os.path

    qtdir = os.path.dirname(os.path.dirname(moc))
    qt3_err = fr"""
scons: warning: Could not detect qt3, using moc executable as a hint \(QT3DIR={qtdir}\)
"""
else:
    qt3_err = r"""
scons: warning: Could not detect qt3, using empty QT3DIR
"""

qt_moved = r"""
scons: \*\*\* Deprecated tool 'qt' renamed to 'qt3'. Please update your build accordingly. 'qt3' will be removed entirely in a future release.
"""

qt3_warnings = [re.compile(qt3_err + TestSCons.file_expr)]
qt_error = [re.compile(qt_moved + TestSCons.file_expr)]

error_output = {
    'icl': intel_warnings,
    'intelc': intel_warnings,
    'qt3': qt3_warnings,
    'qt': qt_error,
}

# An SConstruct for importing Tool names that have illegal characters
# for Python variable names.
indirect_import = """\
DefaultEnvironment(tools=[])
print("Tool %(tool)s (indirect)")
env = Environment(tools = ['%(tool)s'])

SCons = __import__('SCons.Tool.%(tool)s', globals(), locals(), [])
m = getattr(SCons.Tool, '%(tool)s')
env = Environment(tools=[])
m.generate(env)
"""

# An SConstruct for importing Tool names "normally."
direct_import = """\
DefaultEnvironment(tools=[])
print("Tool %(tool)s (direct)")
env = Environment(tools = ['%(tool)s'])

import SCons.Tool.%(tool)s
env = Environment(tools=[])
SCons.Tool.%(tool)s.exists(env)
SCons.Tool.%(tool)s.generate(env)
"""

failures = []
for tool in tools:
    if tool[0] in '0123456789' or '+' in tool or tool in ('as',):
        test.write('SConstruct', indirect_import % locals())
    else:
        test.write('SConstruct', direct_import % locals())
    test.run(stderr=None, status=None)
    stderr = test.stderr()
    if stderr or test.status:
        matched = None
        for expression in error_output.get(tool, []):
            if expression.match(stderr):
                matched = 1
                break
        if not matched:
            print(f"Failed importing '{tool}', stderr:")
            print(stderr)
            failures.append(tool)

test.fail_test(len(failures))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
