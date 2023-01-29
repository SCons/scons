#!/usr/bin/env python
#
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
Test that files are correctly located in the variant directory even when
Scons does not have a global view of all targets.

Sometimes, it might be interesting to not tell scons about every
targets. For example, one might not read in all the SConscipts of a
hierarchical build for a particular invocation of scons. This would be
done to speed-up a partial rebuild when the developer knows that only
a subset of the targets need to be rebuilt.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('dir1')
test.subdir('dir2')

test.write('SConstruct', """\
opts = Variables()
opts.AddVariables(
    BoolVariable('view_all_dependencies', 'View all dependencies', True),
    BoolVariable('duplicate', 'Duplicate sources to variant dir', True)
)

env = Environment(options=opts)
Export('env')

SConscript(dirs='.', variant_dir='build', duplicate=env['duplicate'])
""" % locals())


test.write('SConscript', """\
Import('env')

if env['view_all_dependencies']:
    SConscript(dirs='dir1')

SConscript(dirs='dir2')
""" % locals())

test.write('dir1/SConscript', """\
Import('env')

env.Command('x.cpp', '', Touch('$TARGET'))

env.Object(env.File('x.cpp'))
""" % locals())

test.write('dir2/SConscript', """\
Import('env')

env.Object(env.File('#/build/dir1/x.cpp'))
""" % locals())

test.must_not_exist('build/dir1/x.cpp')


############################################################
#
# Test without duplication
#

# Build everything first.
test.run(arguments = 'duplicate=False view_all_dependencies=True .')
test.must_exist('build/dir1/x.cpp')
test.must_not_contain_any_line(test.stdout(), ["`.' is up to date."])

# Double check that targets are not rebuilt.
test.run(arguments = 'duplicate=False view_all_dependencies=True .')
test.must_exist('build/dir1/x.cpp')
test.must_contain_all_lines(test.stdout(), ["`.' is up to date."])

# Clean-up only the object file
test.run(arguments = 'duplicate=False view_all_dependencies=False -c .')
test.must_exist('build/dir1/x.cpp')

# Rebuild the only object file without seeing all the dependencies.
test.run(arguments = 'duplicate=False view_all_dependencies=False .')
test.must_exist('build/dir1/x.cpp')
test.must_not_contain_any_line(test.stdout(), ["`.' is up to date."])

# Double check that targets are not rebuilt without and with all the
# dependencies.
test.run(arguments = 'duplicate=False view_all_dependencies=False .')
test.must_exist('build/dir1/x.cpp')
test.must_contain_all_lines(test.stdout(), ["`.' is up to date."])

test.run(arguments = 'duplicate=False view_all_dependencies=True .')
test.must_exist('build/dir1/x.cpp')
test.must_contain_all_lines(test.stdout(), ["`.' is up to date."])

# Clean-up everything.
test.run(arguments = 'duplicate=False view_all_dependencies=True -c .')
test.must_not_exist('build/dir1/x.cpp')


############################################################
#
# Test with duplication
#
# FIXME: This can not work for now because there is no way that SCons
# can differentiate between a source that no longer exists and a file
# that has a builder that scons does not know about because scons has
# not parsed all the SConscript of a given project.
#

# # Build everything first.
# test.run(arguments = 'duplicate=True view_all_dependencies=True .')
# test.must_exist('build/dir1/x.cpp')
# test.must_not_contain_any_line(test.stdout(), ["`.' is up to date."])

# # Double check that targets are not rebuilt.
# test.run(arguments = 'duplicate=True view_all_dependencies=True .')
# test.must_exist('build/dir1/x.cpp')
# test.must_contain_all_lines(test.stdout(), ["`.' is up to date."])

# # Clean-up only the object file
# test.run(arguments = 'duplicate=True view_all_dependencies=False -c .')
# test.must_exist('build/dir1/x.cpp')

# # Rebuild the only object file without seeing all the dependencies.
# test.run(arguments = 'duplicate=True view_all_dependencies=False .')
# test.must_exist('build/dir1/x.cpp')
# test.must_not_contain_any_line(test.stdout(), ["`.' is up to date."])

# # Double check that targets are not rebuilt without and with all the
# # dependencies.
# test.run(arguments = 'duplicate=True view_all_dependencies=False .')
# test.must_exist('build/dir1/x.cpp')
# test.must_contain_all_lines(test.stdout(), ["`.' is up to date."])

# test.run(arguments = 'duplicate=True view_all_dependencies=True .')
# test.must_exist('build/dir1/x.cpp')
# test.must_contain_all_lines(test.stdout(), ["`.' is up to date."])

# # Clean-up everything.
# test.run(arguments = 'duplicate=True view_all_dependencies=True -c .')
# test.must_not_exist('build/dir1/x.cpp')


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
