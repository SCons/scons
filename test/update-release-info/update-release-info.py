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
"""
Test bin/update-release-info.py.  Also verify that the original files
have the appropriate triggers to cause the modifications.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import time

import TestRuntest

# Needed to ensure we're using the correct year
this_year = time.localtime()[0]

TestSCons = 'testing/framework/TestSCons.py'.split('/')
README = 'README.rst'.split('/')
README_SF = 'README-SF.rst'.split('/')

ReleaseConfig = 'ReleaseConfig'.split('/')
CHANGES = 'CHANGES.txt'.split('/')
RELEASE = 'RELEASE.txt'.split('/')
Main = 'SCons/Script/Main.py'.split('/')
main_in = 'doc/user/main.in'.split('/')
main_xml = 'doc/user/main.xml'.split('/')

test = TestRuntest.TestRuntest(
    program=os.path.join('bin', 'update-release-info.py'),
    things_to_copy=['bin', 'template']
)
if not os.path.exists(test.program):
    test.skip_test("update-release-info.py is not distributed in this package\n")

expected_stderr = """usage: update-release-info.py [-h] [--verbose] [--timestamp TIMESTAMP]
                              [{develop,release,post}]
update-release-info.py: error: argument mode: invalid choice: 'bad' (choose from 'develop', 'release', 'post')
"""
test.run(arguments='bad', stderr=expected_stderr, status=2)

# Strings to go in ReleaseConfig
combo_strings = [
    # Index 0: version tuple with bad release level
    """version_tuple = (2, 0, 0, 'bad', 0)\n""",
    # Index 1: Python version tuple
    """unsupported_python_version = (2, 6)\n""",
    # Index 2: Python version tuple
    """deprecated_python_version  = (2, 7)\n""",
    # Index 3: alpha version tuple
    """version_tuple = (2, 0, 0, 'a', 0)\n""",
    # Index 4: final version tuple
    """version_tuple = (2, 0, 0, 'final', 0)\n""",
    # Index 5: bad release date
    """release_date = (%d, 12)\n""" % this_year,
    # Index 6: release date (hhhh, mm, dd)
    """release_date = (%d, 12, 21)\n""" % this_year,
    # Index 7: release date (hhhh, mm, dd, hh, mm, ss)
    """release_date = (%d, 12, 21, 12, 21, 12)\n""" % this_year,
]

combo_error = \
    """ERROR: Config file must contain at least version_tuple,
\tunsupported_python_version, and deprecated_python_version.\n"""


def combo_fail(*args, **kw):
    kw.setdefault('status', 1)
    combo_run(*args, **kw)


def combo_run(*args, **kw):
    t = '\n'
    for a in args:
        t += combo_strings[a]

    test.write(ReleaseConfig, t)

    kw.setdefault('stdout', combo_error)
    test.run(**kw)


combo_fail()
combo_fail(0)
combo_fail(1)
combo_fail(2)
combo_fail(0, 1)
combo_fail(0, 2)
combo_fail(1, 2)
combo_fail(0, 1, 2, stdout=
"""ERROR: `bad' is not a valid release type in version tuple;
\tit must be one of a, b, rc, or final\n""")

# We won't need this entry again, so put in a default
combo_strings[0] = combo_strings[1] + combo_strings[2] + combo_strings[3]

combo_fail(0, 5, stdout=
"""ERROR: Invalid release date (%d, 12)
""" % this_year)


def pave(path):
    path = path[:-1]
    if not path or os.path.isdir(os.path.join(*path)):
        return
    pave(path)
    test.subdir(path)


def pave_write(file, contents):
    pave(file)
    test.write(file, contents)


pave_write(CHANGES, """
RELEASE  It doesn't matter what goes here...
""")

pave_write(RELEASE, """
This file has a 3.2.1.beta.20121221 version string in it
""")


pave_write(README, """
These files are a part of 33.22.11:
        scons-33.22.11.tar.gz
        scons-33.22.11.zip

        scons-33.22.11.b.20012122112.suffix
""")

pave_write(README_SF, """
These files are a part of 33.22.11:
        scons-33.22.11.tar.gz
        scons-33.22.11.zip

        scons-33.22.11.b.20012122112.suffix
""")

pave_write(TestSCons, """
copyright_years = Some junk to be overwritten
default_version = More junk
python_version_unsupported = Yep, more junk
python_version_deprecated = And still more
""")

pave_write(Main, """
unsupported_python_version = Not done with junk
deprecated_python_version = It goes on forever
""")

pave_write(main_in, """
TODO
""")

pave_write(main_xml, """
TODO
""")


def updating_run(*args):
    stdout = ''
    for file in args:
        stdout += 'Updating %s...\n' % os.path.join(*file)
    combo_run(0, 7, stdout=stdout, arguments=['--timestamp=yyyymmdd'])


updating_run(ReleaseConfig, CHANGES, RELEASE, README, README_SF,  TestSCons, Main)

test.must_match(CHANGES, """
RELEASE  VERSION/DATE TO BE FILLED IN LATER

      From John Doe:

        - Whatever John Doe did.


RELEASE  It doesn't matter what goes here...
""", mode='r')

test.must_exist(RELEASE)
# TODO Fix checking contents
# test.must_match(RELEASE, """
# This file has a 2.0.0.devyyyymmdd version string in it
# """, mode='r')


years = '2001 - %d' % (this_year + 1)

test.must_match(README, """
These files are a part of 33.22.11:
        scons-2.1.0ayyyymmdd.tar.gz
        scons-2.1.0ayyyymmdd.zip

        scons-2.1.0ayyyymmdd.suffix
""", mode='r')

test.must_match(README_SF, """
These files are a part of 33.22.11:
        scons-2.1.0ayyyymmdd.tar.gz
        scons-2.1.0ayyyymmdd.zip

        scons-2.1.0ayyyymmdd.suffix
""", mode='r')

# should get Python floors from TestSCons module.
test.must_match(TestSCons, """
copyright_years = '%s'
default_version = '2.1.0ayyyymmdd'
python_version_unsupported = (2, 6)
python_version_deprecated = (2, 7)
""" % years, mode='r')

# should get Python floors from TestSCons module.
test.must_match(Main, """
unsupported_python_version = (2, 6)
deprecated_python_version = (2, 7)
""", mode='r')

# TODO: Release option
# TODO: ==============
# TODO:
# TODO: Dates in beta/candidate flow
# TODO:
# TODO: Dates in final flow
# TODO:
# TODO: Post option
# TODO: ===========
# TODO:
# TODO: Dates in post flow
# TODO:
# TODO: Update minor or micro version
# TODO:
# TODO: ReleaseConfig - new version tuple
# TODO:
# TODO: CHANGES - new section
# TODO:
# TODO: RELEASE - new template
# TODO:

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
