#!/usr/bin/env python
#
# __COPYRIGHT__
#
# Count statistics about SCons test and source files.  This must be run
# against a fully-populated tree (for example, one that's been freshly
# checked out).
#
# A test file is anything under the src/ directory that begins with
# 'test_' or ends in 'Tests.py', or anything under the test/ directory
# that ends in '.py'.  Note that runtest.py script does *not*, by default,
# consider the files that begin with 'test_' to be tests, because they're
# tests of SCons packaging and installation, not functional tests of
# SCons code.
#
# A source file is anything under the src/engine/ or src/script/
# directories that ends in '.py' but does NOT begin with 'test_'
# or end in 'Tests.py'.
#
# We report the number of tests and sources, the total number of lines
# in each category, the number of non-blank lines, and the number of
# non-comment lines.  The last figure (non-comment) lines is the most
# interesting one for most purposes.
__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os.path

fmt = "%-16s  %5s  %7s  %9s  %11s  %11s"

class Collection:
  def __init__(self, name, files=None, pred=None):
    self._name = name
    if files is None:
      files = []
    self.files = files
    if pred is None:
      pred = lambda x: True
    self.pred = pred
  def __call__(self, fname):
    return self.pred(fname)
  def __len__(self):
    return len(self.files)
  def collect(self, directory):
    for dirpath, dirnames, filenames in os.walk(directory):
      try: dirnames.remove('.svn')
      except ValueError: pass
      self.files.extend([ os.path.join(dirpath, f)
                          for f in filenames if self.pred(f) ])
  def lines(self):
    try:
      return self._lines
    except AttributeError:
      self._lines = lines = []
      for file in self.files:
          file_lines = open(file).readlines()
          lines.extend([s.lstrip() for s in file_lines])
      return lines
  def non_blank(self):
    return [s for s in self.lines() if s != '']
  def non_comment(self):
    return [s for s in self.lines() if s == '' or s[0] != '#']
  def non_blank_non_comment(self):
    return [s for s in self.lines() if s != '' and s[0] != '#']
  def printables(self):
    return (self._name + ':',
            len(self.files),
            len(self.lines()),
            len(self.non_blank()),
            len(self.non_comment()),
            len(self.non_blank_non_comment()))

def is_Tests_py(x):
    return x[-8:] == 'Tests.py'
def is_test_(x):
    return x[:5] == 'test_'
def is_python(x):
    return x[-3:] == '.py'
def is_source(x):
    return is_python(x) and not is_Tests_py(x) and not is_test_(x)

src_Tests_py_tests = Collection('src/ *Tests.py', pred=is_Tests_py)
src_test_tests = Collection('src/ test_*.py', pred=is_test_)
test_tests = Collection('test/ tests', pred=is_python)
sources = Collection('sources', pred=is_source)

src_Tests_py_tests.collect('src')
src_test_tests.collect('src')
test_tests.collect('test')
sources.collect('src/engine')
sources.collect('src/script')

src_tests = Collection('src/ tests', src_Tests_py_tests.files
                                     + src_test_tests.files)
all_tests = Collection('all tests', src_tests.files + test_tests.files)

def ratio(over, under):
    return "%.2f" % (float(len(over)) / float(len(under)))

print(fmt % ('', '', '', '', '', 'non-blank'))
print(fmt % ('', 'files', 'lines', 'non-blank', 'non-comment', 'non-comment'))
print()
print(fmt % src_Tests_py_tests.printables())
print(fmt % src_test_tests.printables())
print()
print(fmt % src_tests.printables())
print(fmt % test_tests.printables())
print()
print(fmt % all_tests.printables())
print(fmt % sources.printables())
print()
print(fmt % ('ratio:',
             ratio(all_tests, sources),
             ratio(all_tests.lines(), sources.lines()),
             ratio(all_tests.non_blank(), sources.non_blank()),
             ratio(all_tests.non_comment(), sources.non_comment()),
             ratio(all_tests.non_blank_non_comment(),
                   sources.non_blank_non_comment())
            ))
