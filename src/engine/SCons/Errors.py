"""SCons.Errors

This file contains the exception classes used to handle internal
and user errors in SCons.

"""

__revision__ = "Errors.py __REVISION__ __DATE__ __DEVELOPER__"



class InternalError(Exception):
    def __init__(self, args=None):
        self.args = args

class UserError(Exception):
    def __init__(self, args=None):
        self.args = args
