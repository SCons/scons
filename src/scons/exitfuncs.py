"""scons.exitfuncs

Register functions which are executed when scons exits for any reason.

"""

__revision__ = "exitfuncs.py __REVISION__ __DATE__ __DEVELOPER__"



_exithandlers = []
def _run_exitfuncs():
    """run any registered exit functions

    _exithandlers is traversed in reverse order so functions are executed
    last in, first out.
    """

    while _exithandlers:
        func, targs, kargs =  _exithandlers.pop()
        apply(func, targs, kargs)

def register(func, *targs, **kargs):
    """register a function to be executed upon normal program termination

    func - function to be called at exit
    targs - optional arguments to pass to func
    kargs - optional keyword arguments to pass to func
    """
    _exithandlers.append((func, targs, kargs))

import sys

try:
    x = sys.exitfunc

    # if x isn't our own exit func executive, assume it's another
    # registered exit function - append it to our list...
    if x != _run_exitfuncs:
        register(x)

except AttributeError:
    pass

# make our exit function get run by python when it exits:    
sys.exitfunc = _run_exitfuncs

del sys
