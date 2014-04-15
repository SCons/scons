#!/usr/bin/env python
# -*- Python -*-
from __future__ import division

import sys
from math import log, ceil
from optparse import OptionParser
import subprocess

# crack the command line
parser = OptionParser(
             usage="%prog lower-revision upper-revision test_script [arg1 ...]",
             description="Binary search for a bug in a SVN checkout")
(options,script_args) = parser.parse_args()

# make sure we have sufficient parameters
if len(script_args) < 1:
    parser.error("Need a lower revision")
elif len(script_args) < 2:
    parser.error("Need an upper revision")
elif len(script_args) < 3:
    parser.error("Need a script to run")

# extract our starting values
lower = int(script_args[0])
upper = int(script_args[1])
script = script_args[2:]

# print an error message and quit
def error(s):
    print >>sys.stderr, "******", s, "******"
    sys.exit(1)    

# update to the specified version and run test
def testfail(revision):
    "Return true if test fails"
    print "Updating to revision", revision
    if subprocess.call(["svn","up","-qr",str(revision)]) != 0:
        m = "SVN did not update properly to revision %d"
        raise RuntimeError(m % revision)
    return subprocess.call(script,shell=False) != 0

# confirm that the endpoints are different
print "****** Checking upper bracket", upper
upperfails = testfail(upper)
print "****** Checking lower bracket", lower
lowerfails = testfail(lower)
if upperfails == lowerfails:
    error("Upper and lower revisions must bracket the failure")

# binary search for transition
msg = "****** max %d revisions to test (bug bracketed by [%d,%d])"
while upper-lower > 1:
    print msg % (ceil(log(upper-lower,2)), lower, upper)

    mid = (lower + upper)//2
    midfails = testfail(mid)
    if midfails == lowerfails:
        lower = mid
        lowerfails = midfails
    else:
        upper = mid
        upperfails = midfails

# show which revision was first to fail
if upperfails != lowerfails: lower = upper
print "The error was caused by revision", lower

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
