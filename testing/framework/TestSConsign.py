# __COPYRIGHT__

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

__doc__ = """
TestSConsign.py:  a testing framework for the "sconsign" script 
tool.

A TestSConsign environment object is created via the usual invocation:

    test = TestSConsign()

TestSconsign is a subclass of TestSCons, which is a subclass of
TestCommon, which is in turn is a subclass of TestCmd), and hence
has available all of the methods and attributes from those classes,
as well as any overridden or additional methods or attributes defined
in this subclass.
"""

import os
import os.path
import sys

from TestSCons import *
from TestSCons import __all__

__all__.extend([ 'TestSConsign', ])

class TestSConsign(TestSCons):
    """Class for testing the sconsign.py script.

    This provides a common place for initializing sconsign tests,
    eliminating the need to begin every test with the same repeated
    initializations.

    This adds additional methods for running the sconsign script
    without changing the basic ability of the run() method to run
    "scons" itself, since we need to run scons to generate the
    .sconsign files that we want the sconsign script to read.
    """
    def __init__(self, *args, **kw):
        try:
            script_dir = os.environ['SCONS_SCRIPT_DIR']
        except KeyError:
            pass
        else:
            os.chdir(script_dir)
        self.script_dir = os.getcwd()

        TestSCons.__init__(self, *args, **kw)

        self.my_kw = {
            'interpreter' : python,     # imported from TestSCons
        }

        if 'program' not in kw:
            kw['program'] = os.environ.get('SCONS')
            if not kw['program']:
                if os.path.exists('scons'):
                    kw['program'] = 'scons'
                else:
                    kw['program'] = 'scons.py'

        sconsign = os.environ.get('SCONSIGN')
        if not sconsign:
            if os.path.exists(self.script_path('sconsign.py')):
                sconsign = 'sconsign.py'
            elif os.path.exists(self.script_path('sconsign')):
                sconsign = 'sconsign'
            else:
                print("Can find neither 'sconsign.py' nor 'sconsign' scripts.")
                self.no_result()
        self.set_sconsign(sconsign)

    def script_path(self, script):
        return os.path.join(self.script_dir, script)

    def set_sconsign(self, sconsign):
        self.my_kw['program'] = sconsign

    def run_sconsign(self, *args, **kw):
        kw.update(self.my_kw)
        return self.run(*args, **kw)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
