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
from __future__ import division

"""
QMTest classes to support SCons' testing and Aegis-inspired workflow.

Thanks to Stefan Seefeld for the initial code.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

########################################################################
# Imports
########################################################################

import qm
import qm.common
import qm.test.base
from   qm.fields import *
from   qm.executable import *
from   qm.test import database
from   qm.test import test
from   qm.test import resource
from   qm.test import suite
from   qm.test.result import Result
from   qm.test.file_result_stream import FileResultStream
from   qm.test.classes.text_result_stream import TextResultStream
from   qm.test.classes.xml_result_stream import XMLResultStream
from   qm.test.directory_suite import DirectorySuite
from   qm.extension import get_extension_class_name, get_class_arguments_as_dictionary

import dircache
import os
import imp

if sys.platform == 'win32':
    console = 'con'
else:
    console = '/dev/tty'

def Trace(msg):
    open(console, 'w').write(msg)

# QMTest 2.3 hard-codes how it captures the beginning and end time by
# calling the qm.common.format_time_iso() function, which canonicalizes
# the time stamp in one-second granularity ISO format.  In order to get
# sub-second granularity, as well as to use the more precise time.clock()
# function on Windows, we must replace that function with our own.

orig_format_time_iso = qm.common.format_time_iso

if sys.platform == 'win32':
    time_func = time.clock
else:
    time_func = time.time

def my_format_time(time_secs=None):
    return str(time_func())

qm.common.format_time_iso = my_format_time

########################################################################
# Classes
########################################################################

def get_explicit_arguments(e):
    """This function can be removed once QMTest 2.4 is out."""

    # Get all of the arguments.
    arguments = get_class_arguments_as_dictionary(e.__class__)
    # Determine which subset of the 'arguments' have been set
    # explicitly.
    explicit_arguments = {}
    for name, field in arguments.items():
        # Do not record computed fields.
        if field.IsComputed():
            continue
        if name in e.__dict__:
            explicit_arguments[name] = e.__dict__[name]

    return explicit_arguments


def check_exit_status(result, prefix, desc, status):
    """This function can be removed once QMTest 2.4 is out."""

    if sys.platform == "win32" or os.WIFEXITED(status):
        # Obtain the exit code.
        if sys.platform == "win32":
            exit_code = status
        else:
            exit_code = os.WEXITSTATUS(status)
            # If the exit code is non-zero, the test fails.
        if exit_code != 0:
            result.Fail("%s failed with exit code %d." % (desc, exit_code))
            # Record the exit code in the result.
            result[prefix + "exit_code"] = str(exit_code)
            return False

    elif os.WIFSIGNALED(status):
        # Obtain the signal number.
        signal = os.WTERMSIG(status)
        # If the program gets a fatal signal, the test fails .
        result.Fail("%s received fatal signal %d." % (desc, signal))
        result[prefix + "signal"] = str(signal)
        return False
    else:
        # A process should only be able to stop by exiting, or
        # by being terminated with a signal.
        assert None

    return True



class Null(object):
    pass

_null = Null()

sys_attributes = [
    'byteorder',
    'exec_prefix',
    'executable',
    'maxint',
    'maxunicode',
    'platform',
    'prefix',
    'version',
    'version_info',
]

def get_sys_values():
    sys_attributes.sort()
    result = [(k, getattr(sys, k, _null)) for k in sys_attributes]
    result = [t for t in result if not t[1] is _null]
    result = [t[0] + '=' + repr(t[1]) for t in result]
    return '\n '.join(result)

module_attributes = [
    '__version__',
    '__build__',
    '__buildsys__',
    '__date__',
    '__developer__',
]

def get_module_info(module):
    module_attributes.sort()
    result = [(k, getattr(module, k, _null)) for k in module_attributes]
    result = [t for t in result if not t[1] is _null]
    result = [t[0] + '=' + repr(t[1]) for t in result]
    return '\n '.join(result)

environ_keys = [
   'PATH',
   'SCONS',
   'SCONSFLAGS',
   'SCONS_LIB_DIR',
   'PYTHON_ROOT',
   'QTDIR',

   'COMSPEC',
   'INTEL_LICENSE_FILE',
   'INCLUDE',
   'LIB',
   'MSDEVDIR',
   'OS',
   'PATHEXT',
   'SystemRoot',
   'TEMP',
   'TMP',
   'USERNAME',
   'VXDOMNTOOLS',
   'WINDIR',
   'XYZZY'

   'ENV',
   'HOME',
   'LANG',
   'LANGUAGE',
   'LC_ALL',
   'LC_MESSAGES',
   'LOGNAME',
   'MACHINE',
   'OLDPWD',
   'PWD',
   'OPSYS',
   'SHELL',
   'TMPDIR',
   'USER',
]

def get_environment():
    environ_keys.sort()
    result = [(k, os.environ.get(k, _null)) for k in environ_keys]
    result = [t for t in result if not t[1] is _null]
    result = [t[0] + '-' + t[1] for t in result]
    return '\n '.join(result)

class SConsXMLResultStream(XMLResultStream):
    def __init__(self, *args, **kw):
        super(SConsXMLResultStream, self).__init__(*args, **kw)
    def WriteAllAnnotations(self, context):
        # Load (by hand) the SCons modules we just unwrapped so we can
        # extract their version information.  Note that we have to override
        # SCons.Script.main() with a do_nothing() function, because loading up
        # the 'scons' script will actually try to execute SCons...

        src_engine = os.environ.get('SCONS_LIB_DIR')
        if not src_engine:
            src_engine = os.path.join('src', 'engine')
        fp, pname, desc = imp.find_module('SCons', [src_engine])
        SCons = imp.load_module('SCons', fp, pname, desc)

        # Override SCons.Script.main() with a do-nothing function, because
        # loading the 'scons' script will actually try to execute SCons...

        src_engine_SCons = os.path.join(src_engine, 'SCons')
        fp, pname, desc = imp.find_module('Script', [src_engine_SCons])
        SCons.Script = imp.load_module('Script', fp, pname, desc)
        def do_nothing():
            pass
        SCons.Script.main = do_nothing

        scons_file = os.environ.get('SCONS')
        if scons_file:
            src_script, scons_py = os.path.split(scons_file)
            scons = os.path.splitext(scons_py)[0]
        else:
            src_script = os.path.join('src', 'script')
            scons = 'scons'
        fp, pname, desc = imp.find_module(scons, [src_script])
        scons = imp.load_module('scons', fp, pname, desc)
        fp.close()

        self.WriteAnnotation("scons_test.engine", get_module_info(SCons))
        self.WriteAnnotation("scons_test.script", get_module_info(scons))

        self.WriteAnnotation("scons_test.sys", get_sys_values())
        self.WriteAnnotation("scons_test.os.environ", get_environment())

class AegisStream(TextResultStream):
    arguments = [
        qm.fields.IntegerField(
            name = "print_time",
            title = "print individual test times",
            description = """
            """,
            default_value = 0,
        ),
    ]
    def __init__(self, *args, **kw):
        super(AegisStream, self).__init__(*args, **kw)
        self._num_tests = 0
        self._outcomes = {}
        self._outcome_counts = {}
        for outcome in AegisTest.aegis_outcomes:
            self._outcome_counts[outcome] = 0
        self.format = "full"
    def _percent(self, outcome):
        return 100. * self._outcome_counts[outcome] / self._num_tests
    def _aegis_no_result(self, result):
        outcome = result.GetOutcome()
        return (outcome == Result.FAIL and result.get('Test.exit_code') == '2')
    def _DisplayText(self, text):
        # qm.common.html_to_text() uses htmllib, which sticks an extra
        # '\n' on the front of the text.  Strip it and only display
        # the text if there's anything to display.
        text = qm.common.html_to_text(text)
        if text[0] == '\n':
            text = text[1:]
        if text:
            lines = text.splitlines()
            if lines[-1] == '':
                lines = lines[:-1]
            self.file.write('    ' + '\n    '.join(lines) + '\n\n')
    def _DisplayResult(self, result, format):
        test_id = result.GetId()
        kind = result.GetKind()
        if self._aegis_no_result(result):
            outcome = "NO_RESULT"
        else:
            outcome = result.GetOutcome()
        self._WriteOutcome(test_id, kind, outcome)
        self.file.write('\n')
    def _DisplayAnnotations(self, result):
        try:
            self._DisplayText(result["Test.stdout"])
        except KeyError:
            pass
        try:
            self._DisplayText(result["Test.stderr"])
        except KeyError:
            pass
        if self.print_time:
            start = float(result['qmtest.start_time'])
            end = float(result['qmtest.end_time'])
            fmt = "    Total execution time: %.1f seconds\n\n"
            self.file.write(fmt % (end - start))

class AegisChangeStream(AegisStream):
    def WriteResult(self, result):
        test_id = result.GetId()
        if self._aegis_no_result(result):
            outcome = AegisTest.NO_RESULT
        else:
            outcome = result.GetOutcome()
        self._num_tests += 1
        self._outcome_counts[outcome] += 1
        super(AegisStream, self).WriteResult(result)
    def _SummarizeTestStats(self):
        self.file.write("\n")
        self._DisplayHeading("STATISTICS")
        if self._num_tests != 0:
            # We'd like to use the _FormatStatistics() method to do
            # this, but it's wrapped around the list in Result.outcomes,
            # so it's simpler to just do it ourselves.
            print "  %6d        tests total\n" % self._num_tests
            for outcome in AegisTest.aegis_outcomes:
                if self._outcome_counts[outcome] != 0:
                    print "  %6d (%3.0f%%) tests %s" % (
                        self._outcome_counts[outcome],
                        self._percent(outcome),
                        outcome
                    )

class AegisBaselineStream(AegisStream):
    def WriteResult(self, result):
        test_id = result.GetId()
        if self._aegis_no_result(result):
            outcome = AegisTest.NO_RESULT
            self.expected_outcomes[test_id] = Result.PASS
            self._outcome_counts[outcome] += 1
        else:
            self.expected_outcomes[test_id] = Result.FAIL
            outcome = result.GetOutcome()
            if outcome != Result.Fail:
                self._outcome_counts[outcome] += 1
        self._num_tests += 1
        super(AegisStream, self).WriteResult(result)
    def _SummarizeRelativeTestStats(self):
        self.file.write("\n")
        self._DisplayHeading("STATISTICS")
        if self._num_tests != 0:
            # We'd like to use the _FormatStatistics() method to do
            # this, but it's wrapped around the list in Result.outcomes,
            # so it's simpler to just do it ourselves.
            if self._outcome_counts[AegisTest.FAIL]:
                print "  %6d (%3.0f%%) tests as expected" % (
                    self._outcome_counts[AegisTest.FAIL],
                    self._percent(AegisTest.FAIL),
                )
            non_fail_outcomes = list(AegisTest.aegis_outcomes[:])
            non_fail_outcomes.remove(AegisTest.FAIL)
            for outcome in non_fail_outcomes:
                if self._outcome_counts[outcome] != 0:
                    print "  %6d (%3.0f%%) tests unexpected %s" % (
                        self._outcome_counts[outcome],
                        self._percent(outcome),
                        outcome,
                    )

class AegisBatchStream(FileResultStream):
    def __init__(self, arguments):
        super(AegisBatchStream, self).__init__(arguments)
        self._outcomes = {}
    def WriteResult(self, result):
        test_id = result.GetId()
        kind = result.GetKind()
        outcome = result.GetOutcome()
        exit_status = '0'
        if outcome == Result.FAIL:
            exit_status = result.get('Test.exit_code')
        self._outcomes[test_id] = exit_status
    def Summarize(self):
        self.file.write('test_result = [\n')
        for file_name in sorted(self._outcomes.keys()):
            exit_status = self._outcomes[file_name]
            file_name = file_name.replace('\\', '/')
            self.file.write('    { file_name = "%s";\n' % file_name)
            self.file.write('      exit_status = %s; },\n' % exit_status)
        self.file.write('];\n')

class AegisTest(test.Test):
    PASS = "PASS"
    FAIL = "FAIL"
    NO_RESULT = "NO_RESULT"
    ERROR = "ERROR"
    UNTESTED = "UNTESTED"

    aegis_outcomes = (
        PASS, FAIL, NO_RESULT, ERROR, UNTESTED,
    )
    """Aegis test outcomes."""

class Test(AegisTest):
    """Simple test that runs a python script and checks the status
    to determine whether the test passes."""

    script = TextField(title="Script to test")
    topdir = TextField(title="Top source directory")

    def Run(self, context, result):
        """Run the test. The test passes if the command exits with status=0,
        and fails otherwise. The program output is logged, but not validated."""

        command = RedirectedExecutable()
        args = [context.get('python', sys.executable), '-tt', self.script]
        status = command.Run(args, os.environ)
        if not check_exit_status(result, 'Test.', self.script, status):
            # In case of failure record exit code, stdout, and stderr.
            result.Fail("Non-zero exit_code.")
            result["Test.stdout"] = result.Quote(command.stdout)
            result["Test.stderr"] = result.Quote(command.stderr)


class Database(database.Database):
    """Scons test database.
    * The 'src' and 'test' directories are explicit suites.
    * Their subdirectories are implicit suites.
    * All files under 'src/' ending with 'Tests.py' contain tests.
    * All files under 'test/' with extension '.py' contain tests.
    * Right now there is only a single test class, which simply runs
      the specified python interpreter on the given script. To be refined..."""

    srcdir = TextField(title = "Source Directory",
                       description = "The root of the test suite's source tree.")
    _is_generic_database = True

    def is_a_test_under_test(path, t):
        return os.path.splitext(t)[1] == '.py' \
               and os.path.isfile(os.path.join(path, t))

    def is_a_test_under_src(path, t):
        return t[-8:] == 'Tests.py' \
               and os.path.isfile(os.path.join(path, t))

    is_a_test = {
        'src' : is_a_test_under_src,
        'test' : is_a_test_under_test,
    }

    exclude_subdirs = {
        '.svn' : 1,
        'CVS' : 1,
    }

    def is_a_test_subdir(path, subdir):
        if exclude_subdirs.get(subdir):
            return None
        return os.path.isdir(os.path.join(path, subdir))

    def __init__(self, path, arguments):

        self.label_class = "file_label.FileLabel"
        self.modifiable = "false"
        # Initialize the base class.
        super(Database, self).__init__(path, arguments)


    def GetRoot(self):

        return self.srcdir


    def GetSubdirectories(self, directory):

        components = self.GetLabelComponents(directory)
        path = os.path.join(self.GetRoot(), *components)
        if directory:
            dirs = [d for d in dircache.listdir(path)
                    if os.path.isdir(os.path.join(path, d))]
        else:
            dirs = list(self.is_a_test.keys())

        dirs.sort()
        return dirs


    def GetIds(self, kind, directory = "", scan_subdirs = 1):

        components = self.GetLabelComponents(directory)
        path = os.path.join(self.GetRoot(), *components)

        if kind == database.Database.TEST:

            if not components:
                return []

            ids = [self.JoinLabels(directory, t)
                   for t in dircache.listdir(path)
                   if self.is_a_test[components[0]](path, t)]

        elif kind == Database.RESOURCE:
            return [] # no resources yet

        else: # SUITE

            if directory:
                ids = [self.JoinLabels(directory, d)
                       for d in dircache.listdir(path)
                       if os.path.isdir(os.path.join(path, d))]
            else:
                ids = list(self.is_a_test.keys())

        if scan_subdirs:
            for d in dircache.listdir(path):
                if (os.path.isdir(d)):
                    ids.extend(self.GetIds(kind,
                                           self.JoinLabels(directory, d),
                                           True))

        return ids


    def GetExtension(self, id):

        if not id:
            return DirectorySuite(self, id)

        components = self.GetLabelComponents(id)
        path = os.path.join(self.GetRoot(), *components)

        if os.path.isdir(path): # a directory
            return DirectorySuite(self, id)

        elif os.path.isfile(path): # a test

            arguments = {}
            arguments['script'] = path
            arguments['topdir'] = self.GetRoot()

            return Test(arguments, qmtest_id = id, qmtest_database = self)

        else: # nothing else to offer

            return None


    def GetTest(self, test_id):
        """This method can be removed once QMTest 2.4 is out."""

        t = self.GetExtension(test_id)
        if isinstance(t, test.Test):
            return database.TestDescriptor(self,
                                           test_id,
                                           get_extension_class_name(t.__class__),
                                           get_explicit_arguments(t))

        raise database.NoSuchTestError(test_id)

    def GetSuite(self, suite_id):
        """This method can be removed once QMTest 2.4 is out."""

        if suite_id == "":
            return DirectorySuite(self, "")

        s = self.GetExtension(suite_id)
        if isinstance(s, suite.Suite):
            return s

        raise database.NoSuchSuiteError(suite_id)


    def GetResource(self, resource_id):
        """This method can be removed once QMTest 2.4 is out."""

        r = self.GetExtension(resource_id)
        if isinstance(r, resource.Resource):
            return ResourceDescriptor(self,
                                      resource_id,
                                      get_extension_class_name(r.__class__),
                                      get_explicit_arguments(r))

        raise database.NoSuchResourceError(resource_id)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
