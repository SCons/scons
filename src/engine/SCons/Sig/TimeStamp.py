"""SCons.Sig.TimeStamp

The TimeStamp signature package for the SCons software construction
utility.

"""

#
# Copyright (c) 2001 Steven Knight
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

def current(obj, sig):
    """Return whether the objects timestamp is up-to-date.
    """
    return obj.get_signature() >= sig

def collect(signatures):
    """
    Collect a list of timestamps, returning
    the most-recent timestamp from the list 

    signatures - a list of timestamps
    returns - the most recent timestamp
    """

    if len(signatures) == 0:
        return 0
    elif len(signatures) == 1:
        return signatures[0]
    else:
        return max(signatures)

def signature(obj):
    """Generate a timestamp.
    """
    return obj.get_timestamp()

def to_string(signature):
    """Convert a timestamp to a string"""
    return str(signature)

def from_string(string):
    """Convert a string to a timestamp"""
    return int(string)


