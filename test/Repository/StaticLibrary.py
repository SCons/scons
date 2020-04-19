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

import os.path
import TestSCons

_obj = TestSCons._obj
_exe = TestSCons._exe

for implicit_deps in ['0', '1', '2', '\"all\"']:
    test = TestSCons.TestSCons()

    #
    test.subdir('repository', 'work1', 'work2', 'work3')

    #
    workpath_repository = test.workpath('repository')
    repository_aaa_obj = test.workpath('repository', 'aaa' + _obj)
    repository_bbb_obj = test.workpath('repository', 'bbb' + _obj)
    repository_foo_obj = test.workpath('repository', 'foo' + _obj)
    repository_foo = test.workpath('repository', 'foo' + _exe)
    work1_foo = test.workpath('work1', 'foo' + _exe)
    work2_aaa_obj = test.workpath('work2', 'aaa' + _obj)
    work2_foo_obj = test.workpath('work2', 'foo' + _obj)
    work2_foo = test.workpath('work2', 'foo' + _exe)
    work3_aaa_obj = test.workpath('work3', 'aaa' + _obj)
    work3_bbb_obj = test.workpath('work3', 'bbb' + _obj)
    work3_foo = test.workpath('work3', 'foo' + _exe)

    opts = '-Y ' + workpath_repository

    #
    test.write(['repository', 'SConstruct'], """
env = Environment(LIBS = ['xxx'], LIBPATH = '.',
                  IMPLICIT_COMMAND_DEPENDENCIES=%s)
env.Library(target = 'xxx', source = ['aaa.c', 'bbb.c'])
env.Program(target = 'foo', source = 'foo.c')
""" % implicit_deps)

    test.write(['repository', 'aaa.c'], r"""
#include <stdio.h>
#include <stdlib.h>
void
aaa(void)
{
        printf("repository/aaa.c\n");
}
""")

    test.write(['repository', 'bbb.c'], r"""
#include <stdio.h>
#include <stdlib.h>
void
bbb(void)
{
        printf("repository/bbb.c\n");
}
""")

    test.write(['repository', 'foo.c'], r"""
#include <stdio.h>
#include <stdlib.h>
extern void aaa(void);
extern void bbb(void);
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        aaa();
        bbb();
        printf("repository/foo.c\n");
        exit (0);
}
""")

    # Make the repository non-writable,
    # so we'll detect if we try to write into it accidentally.
    test.writable('repository', 0)

    #
    test.run(chdir = 'work1', options = opts, arguments = ".",
             stderr=TestSCons.noisy_ar,
             match=TestSCons.match_re_dotall)

    test.run(program = work1_foo, stdout =
"""repository/aaa.c
repository/bbb.c
repository/foo.c
""")

    test.fail_test(os.path.exists(repository_aaa_obj))
    test.fail_test(os.path.exists(repository_bbb_obj))
    test.fail_test(os.path.exists(repository_foo_obj))
    test.fail_test(os.path.exists(repository_foo))

    test.up_to_date(chdir = 'work1', options = opts, arguments = ".")

    test.write(['work1', 'bbb.c'], r"""
#include <stdio.h>
#include <stdlib.h>
void
bbb(void)
{
        printf("work1/bbb.c\n");
}
""")

    test.run(chdir = 'work1', options = opts, arguments = ".",
             stderr=TestSCons.noisy_ar,
             match=TestSCons.match_re_dotall)

    test.run(program = work1_foo, stdout =
"""repository/aaa.c
work1/bbb.c
repository/foo.c
""")

    test.fail_test(os.path.exists(repository_aaa_obj))
    test.fail_test(os.path.exists(repository_bbb_obj))
    test.fail_test(os.path.exists(repository_foo_obj))
    test.fail_test(os.path.exists(repository_foo))

    test.up_to_date(chdir = 'work1', options = opts, arguments = ".")

    #
    test.writable('repository', 1)

    test.run(chdir = 'repository', options = opts, arguments = ".",
             stderr=TestSCons.noisy_ar,
             match=TestSCons.match_re_dotall)

    test.run(program = repository_foo, stdout =
"""repository/aaa.c
repository/bbb.c
repository/foo.c
""")

    test.fail_test(not os.path.exists(repository_aaa_obj))
    test.fail_test(not os.path.exists(repository_bbb_obj))
    test.fail_test(not os.path.exists(repository_foo_obj))

    test.up_to_date(chdir = 'repository', options = opts, arguments = ".")

    #
    test.writable('repository', 0)

    #
    test.up_to_date(chdir = 'work2', options = opts, arguments = ".")

    test.write(['work2', 'bbb.c'], r"""
#include <stdio.h>
#include <stdlib.h>
void
bbb(void)
{
        printf("work2/bbb.c\n");
}
""")

    test.run(chdir = 'work2', options = opts, arguments = ".",
             stderr=TestSCons.noisy_ar,
             match=TestSCons.match_re_dotall)

    test.run(program = work2_foo, stdout =
"""repository/aaa.c
work2/bbb.c
repository/foo.c
""")

    test.fail_test(os.path.exists(work2_aaa_obj))
    test.fail_test(os.path.exists(work2_foo_obj))

    test.up_to_date(chdir = 'work2', options = opts, arguments = ".")

    #
    test.up_to_date(chdir = 'work3', options = opts, arguments = ".")

    test.write(['work3', 'foo.c'], r"""
#include <stdio.h>
#include <stdlib.h>
extern void aaa(void);
extern void bbb(void);
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        aaa();
        bbb();
        printf("work3/foo.c\n");
        exit (0);
}
""")

    test.run(chdir = 'work3', options = opts, arguments = ".")

    test.run(program = work3_foo, stdout =
"""repository/aaa.c
repository/bbb.c
work3/foo.c
""")

    test.fail_test(os.path.exists(work3_aaa_obj))
    test.fail_test(os.path.exists(work3_bbb_obj))

    test.up_to_date(chdir = 'work3', options = opts, arguments = ".")


#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
