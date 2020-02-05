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

"""
This test verifies:
    1)  that we don't build files when we use the -n, --no-exec,
        --just-print, --dry-run, and --recon options;
    2)  that we don't remove built files when -n is used in
        conjunction with -c;
    3)  that files installed by the Install() method don't get
        installed when -n is used;
    4)  that source files don't get duplicated in a VariantDir
        when -n is used.
    5)  that Configure calls don't build any files. If a file
        needs to be built (i.e. is not up-to-date), a ConfigureError
        is raised.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import re

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.subdir('build', 'src')

test.write('build.py', r"""
import sys
with open(sys.argv[1], 'w') as ofp:
    ofp.write("build.py: %s\n" % sys.argv[1])
""")

test.write('SConstruct', """
DefaultEnvironment(tools=[])
MyBuild = Builder(action=r'%(_python_)s build.py $TARGETS')
env = Environment(BUILDERS={'MyBuild': MyBuild}, tools=[])
env.Tool('install')
env.MyBuild(target='f1.out', source='f1.in')
env.MyBuild(target='f2.out', source='f2.in')
env.Install('install', 'f3.in')
VariantDir('build', 'src', duplicate=1)
SConscript('build/SConscript', "env")
""" % locals())

test.write(['src', 'SConscript'], """
Import("env")
env.MyBuild(target='f4.out', source='f4.in')
""")

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")
test.write('f3.in', "f3.in\n")
test.write(['src', 'f4.in'], "src/f4.in\n")

args = 'f1.out f2.out'
expect = test.wrap_stdout("""\
%(_python_)s build.py f1.out
%(_python_)s build.py f2.out
""" % locals())

test.run(arguments=args, stdout=expect)
test.fail_test(not os.path.exists(test.workpath('f1.out')))
test.fail_test(not os.path.exists(test.workpath('f2.out')))

test.unlink('f1.out')
test.unlink('f2.out')

test.run(arguments='-n ' + args, stdout=expect)
test.fail_test(os.path.exists(test.workpath('f1.out')))
test.fail_test(os.path.exists(test.workpath('f2.out')))

test.run(arguments='--no-exec ' + args, stdout=expect)
test.fail_test(os.path.exists(test.workpath('f1.out')))
test.fail_test(os.path.exists(test.workpath('f2.out')))

test.run(arguments='--just-print ' + args, stdout=expect)
test.fail_test(os.path.exists(test.workpath('f1.out')))
test.fail_test(os.path.exists(test.workpath('f2.out')))

test.run(arguments='--dry-run ' + args, stdout=expect)
test.fail_test(os.path.exists(test.workpath('f1.out')))
test.fail_test(os.path.exists(test.workpath('f2.out')))

test.run(arguments='--recon ' + args, stdout=expect)
test.fail_test(os.path.exists(test.workpath('f1.out')))
test.fail_test(os.path.exists(test.workpath('f2.out')))

test.run(arguments=args)
test.fail_test(not os.path.exists(test.workpath('f1.out')))

# Test that SCons does not write a modified .sconsign when -n is used.
expect = test.wrap_stdout("""\
%(_python_)s build.py f1.out
""" % locals())
test.unlink('.sconsign.dblite')
test.write('f1.out', "X1.out\n")
test.run(arguments='-n f1.out', stdout=expect)
test.run(arguments='-n f1.out', stdout=expect)

expect = test.wrap_stdout("Removed f1.out\nRemoved f2.out\n", cleaning=1)

test.run(arguments='-n -c ' + args, stdout=expect)

test.run(arguments='-c -n ' + args, stdout=expect)

test.fail_test(not os.path.exists(test.workpath('f1.out')))
test.fail_test(not os.path.exists(test.workpath('f2.out')))

#
install_f3_in = os.path.join('install', 'f3.in')
expect = test.wrap_stdout('Install file: "f3.in" as "%s"\n' % install_f3_in)

test.run(arguments='-n install', stdout=expect)
test.fail_test(os.path.exists(test.workpath('install', 'f3.in')))

test.run(arguments='install', stdout=expect)
test.fail_test(not os.path.exists(test.workpath('install', 'f3.in')))

test.write('f3.in', "f3.in again\n")

test.run(arguments='-n install', stdout=expect)
test.fail_test(not os.path.exists(test.workpath('install', 'f3.in')))

# Make sure duplicate source files in a VariantDir aren't created
# when the -n option is used.

# First, make sure none of the previous non-dryrun invocations caused
# the build directory to be populated.  Processing of the
# src/SConscript (actually build/SConscript) will reference f4.in as a
# source, causing a Node object to be built for "build/f4.in".
# Creating the node won't cause "build/f4.in" to be created from
# "src/f4.in", but that *is* a side-effect of calling the exists()
# method on that node, which may happen via other processing.
# Therefore add this conditional removal to ensure  a clean setting
# before running this test.

if os.path.exists(test.workpath('build', 'f4.in')):
    test.unlink(test.workpath('build', 'f4.in'))

test.run(arguments='-n build')
test.fail_test(os.path.exists(test.workpath('build', 'f4.in')))

# test Configure-calls in conjunction with -n
test.subdir('configure')
test.set_match_function(TestSCons.match_re_dotall)
test.set_diff_function(TestSCons.diff_re)
test.write('configure/SConstruct', """\
DefaultEnvironment(tools=[])
def CustomTest(context):
    def userAction(target,source,env):
        import shutil
        shutil.copyfile( str(source[0]), str(target[0]))
    def strAction(target,source,env):
        return "cp " + str(source[0]) + " " + str(target[0])
    context.Message("Executing Custom Test ... " )
    (ok, msg) = context.TryAction(Action(userAction,strAction),
                                  "Hello World", ".in")
    context.Result(ok)
    return ok

env = Environment(tools=[])
conf = Configure(env,
                 custom_tests={'CustomTest':CustomTest},
                 conf_dir="config.test",
                 log_file="config.log")
if not conf.CustomTest():
    Exit(1)
else:
    env = conf.Finish()
""")
# test that conf_dir isn't created and an error is raised
stderr = r"""
scons: \*\*\* Cannot create configure directory "config\.test" within a dry-run\.
File \S+, line \S+, in \S+
"""
test.run(arguments="-n", stderr=stderr, status=2,
         chdir=test.workpath("configure"))
test.fail_test(os.path.exists(test.workpath("configure", "config.test")))
test.fail_test(os.path.exists(test.workpath("configure", "config.log")))

# test that targets are not built, if conf_dir exists.
# verify that .cache and config.log are not created.
# an error should be raised
stderr = r"""
scons: \*\*\* Cannot update configure test "%s" within a dry-run\.
File \S+, line \S+, in \S+
""" % re.escape(os.path.join("config.test", "conftest_b10a8db164e0754105b7a99be72e3fe5_0.in"))
test.subdir(['configure', 'config.test'])
test.run(arguments="-n", stderr=stderr, status=2,
         chdir=test.workpath("configure"))
test.fail_test(os.path.exists(test.workpath("configure", "config.test",
                                            ".cache")))
test.fail_test(os.path.exists(test.workpath("configure", "config.test",
                                            "conftest_0")))
test.fail_test(os.path.exists(test.workpath("configure", "config.test",
                                            "conftest_0.in")))
test.fail_test(os.path.exists(test.workpath("configure", "config.log")))

# test that no error is raised, if all targets are up-to-date. In this
# case .cache and config.log shouldn't be created
stdout = test.wrap_stdout(build_str="scons: `.' is up to date.\n",
                          read_str=r"""Executing Custom Test ... \(cached\) yes
""")
test.run(status=0, chdir=test.workpath("configure"))
log1_mtime = os.path.getmtime(test.workpath("configure", "config.log"))
test.run(stdout=stdout, arguments="-n", status=0,
         chdir=test.workpath("configure"))
log2_mtime = os.path.getmtime(test.workpath("configure", "config.log"))
test.fail_test(log1_mtime != log2_mtime)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
