#!/usr/bin/env python
#
# Quick script to process the *summary* output from SCons.Debug.caller()
# and print indented calling trees with call counts.
#
# The way to use this is to add something like the following to a function
# for which you want information about who calls it and how many times:
#
#       from SCons.Debug import caller
#       caller(0, 1, 2, 3, 4, 5)
#
# Each integer represents how many stack frames back SCons will go
# and capture the calling information, so in the above example it will
# capture the calls six levels up the stack in a central dictionary.
#
# At the end of any run where SCons.Debug.caller() is used, SCons will
# print a summary of the calls and counts that looks like the following:
#
#       Callers of Node/__init__.py:629(calc_signature):
#                1 Node/__init__.py:683(calc_signature)
#       Callers of Node/__init__.py:676(gen_binfo):
#                6 Node/FS.py:2035(current)
#                1 Node/__init__.py:722(get_bsig)
#
# If you cut-and-paste that summary output and feed it to this script
# on standard input, it will figure out how these entries hook up and
# print a calling tree for each one looking something like:
#
#   Node/__init__.py:676(gen_binfo)
#     Node/FS.py:2035(current)                                           6
#       Taskmaster.py:253(make_ready_current)                           18
#         Script/Main.py:201(make_ready)                                18
#
# Note that you should *not* look at the call-count numbers in the right
# hand column as the actual number of times each line *was called by*
# the function on the next line.  Rather, it's the *total* number
# of times each function was found in the call chain for any of the
# calls to SCons.Debug.caller().  If you're looking at more than one
# function at the same time, for example, their counts will intermix.
# So use this to get a *general* idea of who's calling what, not for
# fine-grained performance tuning.
import sys

class Entry:
    def __init__(self, file_line_func):
        self.file_line_func = file_line_func
        self.called_by = []
        self.calls = []

AllCalls = {}

def get_call(flf):
    try:
        e = AllCalls[flf]
    except KeyError:
        e = AllCalls[flf] = Entry(flf)
    return e

prefix = 'Callers of '

c = None
for line in sys.stdin.readlines():
    if line[0] == '#':
        pass
    elif line[:len(prefix)] == prefix:
        c = get_call(line[len(prefix):-2])
    else:
        num_calls, flf = line.strip().split()
        e = get_call(flf)
        c.called_by.append((e, num_calls))
        e.calls.append(c)

stack = []

def print_entry(e, level, calls):
    print('%-72s%6s' % ((' '*2*level) + e.file_line_func, calls))
    if e in stack:
        print((' '*2*(level+1))+'RECURSION')
        print()
    elif e.called_by:
        stack.append(e)
        for c in e.called_by:
            print_entry(c[0], level+1, c[1])
        stack.pop()
    else:
        print()

for e in [ e for e in list(AllCalls.values()) if not e.calls ]:
    print_entry(e, 0, '')

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
