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
Verify that we can print .sconsign files with Configure context
info in them (which have different BuildInfo entries).
"""

import os
import re

import TestSCons
import TestSConsign

_obj = TestSCons._obj

test = TestSConsign.TestSConsign(match = TestSConsign.match_re,
                                 diff = TestSConsign.diff_re)

# Note: Here we pass the full search PATH of our current system to
# the detect() method. This way we try to ensure that we find the same
# compiler executable as the SConstruct below, which uses
# os.environ['PATH'] too.
CC = test.detect('CC', ENV={'PATH' : os.environ.get('PATH','')}, norm=1)
CC_dir, CC_file = os.path.split(CC)

CC = re.escape(CC)
CC_dir = re.escape(os.path.normcase(CC_dir))
CC_file = re.escape(CC_file)

# Note:  We don't use os.path.join() representations of the file names
# in the expected output because paths in the .sconsign files are
# canonicalized to use / as the separator.


test.write('SConstruct', """
import os
env = Environment(ENV={'PATH' : os.environ.get('PATH','')})
conf = Configure(env)
r1 = conf.CheckCHeader( 'math.h' )
env = conf.Finish()
""")

test.run(arguments = '.')

sig_re = r'[0-9a-fA-F]{32}'
date_re = r'\S+ \S+ [ \d]\d \d\d:\d\d:\d\d \d\d\d\d'
_sconf_temp_conftest_0_c = '.sconf_temp/conftest_%(sig_re)s_0.c'%locals()

# Note:  There's a space at the end of the '.*': line, because the
# Value node being printed actually begins with a newline.  It would
# probably be good to change that to a repr() of the contents.
expect = r"""=== .:
SConstruct: None \d+ \d+
=== .sconf_temp:
conftest_%(sig_re)s_0.c:
        '.*': 
#include "math.h"


        %(sig_re)s \[.*\]
conftest_%(sig_re)s_0_%(sig_re)s%(_obj)s:
        %(_sconf_temp_conftest_0_c)s: %(sig_re)s \d+ \d+
        %(CC)s: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
=== %(CC_dir)s:
%(CC_file)s: %(sig_re)s \d+ \d+
""" % locals()

test.run_sconsign(arguments = ".sconsign",
                  stdout = expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
