# MIT License
#
# Copyright The SCons Foundation
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

"""
A testing framework for the scons-time.py script

A TestSCons_time environment object is created via the usual invocation:

    test = TestSCons_time()

TestSCons_time is a subclass of TestCommon, which is in turn is a subclass
of TestCmd), and hence has available all of the methods and attributes
from those classes, as well as any overridden or additional methods or
attributes defined in this subclass.
"""

import os
import os.path
import sys

from TestCommon import *
from TestCommon import __all__
# some of the scons_time tests may need regex-based matching:
from TestSCons import search_re, search_re_in_list

__all__.extend(['TestSCons_time',])

SConstruct = """\
import os
print("SConstruct file directory:", os.getcwd())
"""

scons_py = """\
#!/usr/bin/env python
import os
import sys

def write_args(fp, args):
    fp.write(args[0] + '\\n')
    for arg in args[1:]:
        fp.write('    ' + arg + '\\n')

write_args(sys.stdout, sys.argv)
for arg in sys.argv[1:]:
    if arg[:10] == '--profile=':
        with open(arg[10:], 'w') as profile:
            profile.write('--profile\\n')
            write_args(profile, sys.argv)
        break
sys.stdout.write('SCONS_LIB_DIR = ' + os.environ['SCONS_LIB_DIR'] + '\\n')
with open('SConstruct', 'r') as f:
    script = f.read()
exec(script)
"""

svn_py = f"""#!/usr/bin/env python
import os
import sys

dir = sys.argv[-1]
script_dir = dir + '/scripts'
os.makedirs(script_dir)
with open(script_dir + '/scons.py', 'w') as f:
    f.write(r'''{scons_py}''')
"""


git_py = f"""#!/usr/bin/env python
import os
import sys

dir = sys.argv[-1]
script_dir = dir + '/scripts'
os.makedirs(script_dir)
with open(script_dir + '/scons.py', 'w') as f:
    f.write(r'''{scons_py}''')
"""


logfile_contents = """\
Memory before reading SConscript files:  100%(index)s
Memory after reading SConscript files:  200%(index)s
Memory before building targets:  300%(index)s
Memory after building targets:  400%(index)s
Object counts:
       pre-   post-    pre-   post-   
       read    read   build   build   Class
       101%(index)s    102%(index)s    103%(index)s    104%(index)s   Action.CommandAction
       201%(index)s    202%(index)s    203%(index)s    204%(index)s   Action.CommandGeneratorAction
       301%(index)s    302%(index)s    303%(index)s    304%(index)s   Action.FunctionAction
       401%(index)s    402%(index)s    403%(index)s    404%(index)s   Action.LazyAction
       501%(index)s    502%(index)s    503%(index)s    504%(index)s   Action.ListAction
       601%(index)s    602%(index)s    603%(index)s    604%(index)s   Builder.BuilderBase
       701%(index)s    702%(index)s    703%(index)s    704%(index)s   Builder.CompositeBuilder
       801%(index)s    802%(index)s    803%(index)s    804%(index)s   Builder.ListBuilder
       901%(index)s    902%(index)s    903%(index)s    904%(index)s   Builder.MultiStepBuilder
      1001%(index)s   1002%(index)s   1003%(index)s   1004%(index)s   Builder.OverrideWarner
      1101%(index)s   1102%(index)s   1103%(index)s   1104%(index)s   Environment.Base
      1201%(index)s   1202%(index)s   1203%(index)s   1204%(index)s   Environment.EnvironmentClone
      1301%(index)s   1302%(index)s   1303%(index)s   1304%(index)s   Environment.OverrideEnvironment
      1401%(index)s   1402%(index)s   1403%(index)s   1404%(index)s   Executor.Executor
      1501%(index)s   1502%(index)s   1503%(index)s   1504%(index)s   Node.FS
      1601%(index)s   1602%(index)s   1603%(index)s   1604%(index)s   Node.FS.Base
      1701%(index)s   1702%(index)s   1703%(index)s   1704%(index)s   Node.FS.Dir
      1801%(index)s   1802%(index)s   1803%(index)s   1804%(index)s   Node.FS.File
      1901%(index)s   1902%(index)s   1904%(index)s   1904%(index)s   Node.FS.RootDir
      2001%(index)s   2002%(index)s   2003%(index)s   2004%(index)s   Node.Node
Total build time: 11.123456 seconds
Total SConscript file execution time: 22.234567 seconds
Total SCons execution time: 33.345678 seconds
Total command execution time: 44.456789 seconds
"""


profile_py = """\
%(body)s

import profile

try: dispatch = profile.Profile.dispatch
except AttributeError: pass
else: dispatch['c_exception'] = profile.Profile.trace_dispatch_return

prof = profile.Profile()
prof.runcall(%(call)s)
prof.dump_stats(r'%(profile_name)s')
"""


class TestSCons_time(TestCommon):
    """Class for testing the scons-time script.

    This provides a common place for initializing scons-time tests,
    eliminating the need to begin every test with the same repeated
    initializations.
    """

    def __init__(self, **kw):
        """Initialize an SCons_time testing object.

        If they're not overridden by keyword arguments, this
        initializes the object with the following default values:

                program = 'scons-time'
                interpreter = ['python', '-tt']
                match = match_exact
                workdir = ''

        The workdir value means that, by default, a temporary workspace
        directory is created for a TestSCons_time environment.
        In addition, this method changes directory (chdir) to the
        workspace directory, so an explicit "chdir = '.'" on all of the
        run() method calls is not necessary.
        """

        self.orig_cwd = os.getcwd()
        try:
            script_dir = os.environ['SCONS_TOOLS_DIR']
        except KeyError:
            pass
        else:
            os.chdir(script_dir)
        if 'program' not in kw:
            p = os.environ.get('SCONS_TIME')
            if not p:
                p = 'scons-time'
                if not os.path.exists(p):
                    p = 'scons-time.py'
            kw['program'] = p

        if 'interpreter' not in kw:
            kw['interpreter'] = [python,]

        if 'match' not in kw:
            kw['match'] = match_exact

        if 'workdir' not in kw:
            kw['workdir'] = ''

        super().__init__(**kw)

    def archive_split(self, path):
        if path[-7:] == '.tar.gz':
            return path[:-7], path[-7:]
        else:
            return os.path.splitext(path)

    def fake_logfile(self, logfile_name, index=0):
        self.write(self.workpath(logfile_name), logfile_contents % locals())

    def profile_data(self, profile_name, python_name, call, body):
        profile_name = self.workpath(profile_name)
        python_name = self.workpath(python_name)
        d = {
            'profile_name'  : profile_name,
            'python_name'   : python_name,
            'call'          : call,
            'body'          : body,
        }
        self.write(python_name, profile_py % d)
        self.run(program = python_name, interpreter = sys.executable)

    def tempdir_re(self, *args):
        """
        Returns a regular expression to match a scons-time
        temporary directory.
        """
        import re
        import tempfile

        sep = re.escape(os.sep)
        tempdir = tempfile.gettempdir()

        try:
            realpath = os.path.realpath
        except AttributeError:
            pass
        else:
            tempdir = realpath(tempdir)

        args = (tempdir, 'scons-time-',) + args
        x = os.path.join(*args)
        x = re.escape(x)
        x = x.replace('time\\-', f'time\\-[^{sep}]*')
        return x

    def write_fake_scons_py(self):
        self.subdir('scripts')
        self.write('scripts/scons.py', scons_py)

    def write_fake_svn_py(self, name):
        name = self.workpath(name)
        self.write(name, svn_py)
        os.chmod(name, 0o755)
        return name

    def write_fake_git_py(self, name):
        name = self.workpath(name)
        self.write(name, git_py)
        os.chmod(name, 0o755)
        return name

    def write_sample_directory(self, archive, dir, files):
        dir = self.workpath(dir)
        for name, content in files:
            path = os.path.join(dir, name)
            d, f = os.path.split(path)
            if not os.path.isdir(d):
                os.makedirs(d)
            with open(path, 'w') as f:
                f.write(content)
        return dir

    def write_sample_tarfile(self, archive, dir, files):
        import shutil
        try:
            import tarfile
        except ImportError:
            self.skip_test('no tarfile module\n', from_framework=True)
        else:
            base, suffix = self.archive_split(archive)

            mode = {
                '.tar'      : 'w',
                '.tar.gz'   : 'w:gz',
                '.tgz'      : 'w:gz',
            }

            tar = tarfile.open(archive, mode[suffix])
            for name, content in files:
                path = os.path.join(dir, name)
                with open(path, 'wb') as f:
                    f.write(bytearray(content,'utf-8'))
                tarinfo = tar.gettarinfo(path, path)
                tarinfo.uid = 111
                tarinfo.gid = 111
                tarinfo.uname = 'fake_user'
                tarinfo.gname = 'fake_group'
                with open(path, 'rb') as f:
                    tar.addfile(tarinfo, f)
            tar.close()
            shutil.rmtree(dir)
            return self.workpath(archive)

    def write_sample_zipfile(self, archive, dir, files):
        import shutil
        try:
            import zipfile
        except ImportError:

            sys.stderr.write('no zipfile module\n')
            self.no_result()

        else:

            zip = zipfile.ZipFile(archive, 'w')
            for name, content in files:
                path = os.path.join(dir, name)
                with open(path, 'w') as f:
                    f.write(content)
                zip.write(path)
            zip.close()
            shutil.rmtree(dir)
            return self.workpath(archive)

    sample_project_files = [
        ('SConstruct',  SConstruct),
    ]

    def write_sample_project(self, archive, dir=None):
        base, suffix = self.archive_split(archive)

        write_sample = {
            '.tar'      : self.write_sample_tarfile,
            '.tar.gz'   : self.write_sample_tarfile,
            '.tgz'      : self.write_sample_tarfile,
            '.zip'      : self.write_sample_zipfile,
        }.get(suffix, self.write_sample_directory)

        if not dir:
            dir = base

        os.mkdir(dir)
        path = write_sample(archive, dir, self.sample_project_files)

        return path

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
