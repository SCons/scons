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
Functions and data for timing different idioms for fetching a keyword
value from a pair of dictionaries for local and global values.  This was
used to select how to most efficiently expand single $KEYWORD strings
in SCons/Subst.py (StringSubber and ListSubber).
"""

def Func1(var, gvars, lvars):
    """lvars try:-except:, gvars try:-except:"""
    for i in IterationList:
        try:
            x = lvars[var]
        except KeyError:
            try:
                x = gvars[var]
            except KeyError:
                x = ''

def Func2(var, gvars, lvars):
    """lvars membership test, gvars try:-except:"""
    for i in IterationList:
        if var in lvars:
            x = lvars[var]
        else:
            try:
                x = gvars[var]
            except KeyError:
                x = ''

def Func3(var, gvars, lvars):
    """lvars membership test, gvars membership test)"""
    for i in IterationList:
        if var in lvars:
            x = lvars[var]
        elif var in gvars:
            x = gvars[var]
        else:
            x = ''

def Func4(var, gvars, lvars):
    """eval()"""
    for i in IterationList:
        try:
            x = eval(var, gvars, lvars)
        except NameError:
            x = ''

def Func5(var, gvars, lvars):
    """Chained get with default values"""
    for i in IterationList:
        x = lvars.get(var, gvars.get(var, ''))


# Data to pass to the functions on each run.  Each entry is a
# three-element tuple:
#
#   (
#       "Label to print describing this data run",
#       ('positional', 'arguments'),
#       {'keyword' : 'arguments'},
#   ),

Data = [
    (
        "Neither in gvars or lvars",
        ('x', {}, {}),
        {},
    ),
    (
        "Missing from lvars, found in gvars",
        ('x', {'x':1}, {}),
        {},
    ),
    (
        "Found in lvars",
        ('x', {'x':1}, {'x':2}),
        {},
    ),
]
