"""SCons.Debug

Code for debugging SCons internal things.  Not everything here is
guaranteed to work all the way back to Python 1.5.2, and shouldn't be
needed by most users.

"""

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


# Recipe 14.10 from the Python Cookbook.
import string
import sys
try:
    import weakref
except ImportError:
    def logInstanceCreation(instance, name=None):
        pass
else:
    def logInstanceCreation(instance, name=None):
        if name is None:
            name = instance.__class__.__name__
        if not tracked_classes.has_key(name):
            tracked_classes[name] = []
        tracked_classes[name].append(weakref.ref(instance))



tracked_classes = {}

def string_to_classes(s):
    if s == '*':
        c = tracked_classes.keys()
        c.sort()
        return c
    else:
        return string.split(s)

def fetchLoggedInstances(classes="*"):
    classnames = string_to_classes(classes)
    return map(lambda cn: (cn, len(tracked_classes[cn])), classnames)
  
def countLoggedInstances(classes, file=sys.stdout):
    for classname in string_to_classes(classes):
        file.write("%s: %d\n" % (classname, len(tracked_classes[classname])))

def listLoggedInstances(classes, file=sys.stdout):
    for classname in string_to_classes(classes):
        file.write('\n%s:\n' % classname)
        for ref in tracked_classes[classname]:
            obj = ref()
            if obj is not None:
                file.write('    %s\n' % repr(obj))

def dumpLoggedInstances(classes, file=sys.stdout):
    for classname in string_to_classes(classes):
        file.write('\n%s:\n' % classname)
        for ref in tracked_classes[classname]:
            obj = ref()
            if obj is not None:
                file.write('    %s:\n' % obj)
                for key, value in obj.__dict__.items():
                    file.write('        %20s : %s\n' % (key, value))



if sys.platform[:5] == "linux":
    # Linux doesn't actually support memory usage stats from getrusage().
    def memory():
        mstr = open('/proc/self/stat').read()
        mstr = string.split(mstr)[22]
        return int(mstr)
else:
    try:
        import resource
    except ImportError:
        def memory():
            return 0
    else:
        def memory():
            res = resource.getrusage(resource.RUSAGE_SELF)
            return res[4]



caller_dicts = {}

def caller(back=0):
    import traceback
    tb = traceback.extract_stack(limit=3+back)
    key = tb[1][:3]
    try:
        entry = caller_dicts[key]
    except KeyError:
        entry = caller_dicts[key] = {}
    key = tb[0][:3]
    try:
        entry[key] = entry[key] + 1
    except KeyError:
        entry[key] = 1
    return '%s:%d(%s)' % func_shorten(key)

def dump_caller_counts(file=sys.stdout):
    keys = caller_dicts.keys()
    keys.sort()
    for k in keys:
        file.write("Callers of %s:%d(%s):\n" % func_shorten(k))
        counts = caller_dicts[k]
        callers = counts.keys()
        callers.sort()
        for c in callers:
            #file.write("    counts[%s] = %s\n" % (c, counts[c]))
            t = ((counts[c],) + func_shorten(c))
            file.write("    %6d %s:%d(%s)\n" % t)

shorten_list = [
    ( '/scons/SCons/',          1),
    ( '/src/engine/SCons/',     1),
    ( '/usr/lib/python',        0),
]

def func_shorten(func_tuple):
    f = func_tuple[0]
    for t in shorten_list:
        i = string.find(f, t[0])
        if i >= 0:
            if t[1]:
                i = i + len(t[0])
            f = f[i:]
            break
    return (f,)+func_tuple[1:]



TraceFP = {}
TraceDefault = '/dev/tty'

def Trace(msg, file=None, mode='a'):
    """Write a trace a message to a file.  Whenever a file is specified,
    it becomes the default for the next call to Trace()."""
    global TraceDefault
    if file is None:
        file = TraceDefault
    else:
        TraceDefault = file
    try:
        fp = TraceFP[file]
    except KeyError:
        try:
            fp = TraceFP[file] = open(file, mode)
        except TypeError:
            # Assume we were passed an open file pointer.
            fp = file
    fp.write(msg)
