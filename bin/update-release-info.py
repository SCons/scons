#!/usr/bin/env python
"""
This program takes information about a release in the ReleaseConfig file
and inserts the information in various files.  It helps to keep the files
in sync because it never forgets which files need to be updated, nor what
information should be inserted in each file.

It takes one parameter that says what the mode of update should be, which
may be one of 'develop', 'release', or 'post'.

In 'develop' mode, which is what someone would use as part of their own
development practices, the release type is forced to be 'alpha' and the
patch level is the string 'yyyymmdd'.  Otherwise, it's the same as the
'release' mode.

In 'release' mode, the release type is taken from ReleaseConfig and the
patch level is calculated from the release date for non-final runs and
taken from the version tuple for final runs.  It then inserts information
in various files:
  - The RELEASE header line in src/CHANGES.txt and src/Announce.txt.
  - The version string at the top of src/RELEASE.txt.
  - The version string in the 'default_version' variable in SConstruct
    and testing/framework/TestSCons.py.
  - The copyright years in SConstruct and testing/framework/TestSCons.py.
  - The month and year (used for documentation) in SConstruct.
  - The unsupported and deprecated Python floors in testing/framework/TestSCons.py
    and src/engine/SCons/Script/Main.py
  - The version string in the filenames in README.

In 'post' mode, files are prepared for the next release cycle:
  - In ReleaseConfig, the version tuple is updated for the next release
    by incrementing the release number (either minor or micro, depending
    on the branch) and resetting release type to 'alpha'.
  - A blank template replaces src/RELEASE.txt.
  - A new section to accumulate changes is added to src/CHANGES.txt and
    src/Announce.txt.
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
from __future__ import print_function

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import sys
import time
import re

DEBUG = os.environ.get('DEBUG', 0)

# Evaluate parameter

if len(sys.argv) < 2:
    mode = 'develop'
else:
    mode = sys.argv[1]
    if mode not in ['develop', 'release', 'post']:
        print(("""ERROR: `%s' as a parameter is invalid; it must be one of
\tdevelop, release, or post.  The default is develop.""" % mode))
        sys.exit(1)

# Get configuration information

config = dict()
exec(open('ReleaseConfig').read(), globals(), config)

try:
    version_tuple = config['version_tuple']
    unsupported_version = config['unsupported_python_version']
    deprecated_version = config['deprecated_python_version']
except KeyError:
    print('''ERROR: Config file must contain at least version_tuple,
\tunsupported_python_version, and deprecated_python_version.''')
    sys.exit(1)
if DEBUG: print('version tuple', version_tuple)
if DEBUG: print('unsupported Python version', unsupported_version)
if DEBUG: print('deprecated Python version', deprecated_version)

try:
    release_date = config['release_date']
except KeyError:
    release_date = time.localtime()[:6]
else:
    if len(release_date) == 3:
        release_date = release_date + time.localtime()[3:6]
    if len(release_date) != 6:
        print('''ERROR: Invalid release date''', release_date)
        sys.exit(1)
if DEBUG: print('release date', release_date)

if mode == 'develop' and version_tuple[3] != 'alpha':
    version_tuple ==  version_tuple[:3] + ('alpha', 0)
if len(version_tuple) > 3 and version_tuple[3] != 'final':
    if mode == 'develop':
        version_tuple = version_tuple[:4] + ('yyyymmdd',)
    else:
        yyyy,mm,dd,_,_,_ = release_date
        version_tuple = version_tuple[:4] + ((yyyy*100 + mm)*100 + dd,)
version_string = '.'.join(map(str, version_tuple))
if len(version_tuple) > 3:
    version_type = version_tuple[3]
else:
    version_type = 'final'
if DEBUG: print('version string', version_string)

if version_type not in ['alpha', 'beta', 'candidate', 'final']:
    print(("""ERROR: `%s' is not a valid release type in version tuple;
\tit must be one of alpha, beta, candidate, or final""" % version_type))
    sys.exit(1)

try:
    month_year = config['month_year']
except KeyError:
    if version_type == 'alpha':
        month_year = 'MONTH YEAR'
    else:
        month_year =  time.strftime('%B %Y', release_date + (0,0,0))
if DEBUG: print('month year', month_year)

try:
    copyright_years = config['copyright_years']
except KeyError:
    copyright_years = '2001 - %d'%(release_date[0] + 1)
if DEBUG: print('copyright years', copyright_years)

class UpdateFile(object):
    """
    XXX
    """

    def __init__(self, file, orig = None):
        '''
        '''
        if orig is None: orig = file
        try:
            self.content = open(orig, 'r').read()
        except IOError:
            # Couldn't open file; don't try to write anything in __del__
            self.file = None
            raise
        else:
            self.file = file
            if file == orig:
                # so we can see if it changed
                self.orig = self.content
            else:
                # pretend file changed
                self.orig = ''

    def sub(self, pattern, replacement, count = 1):
        '''
        XXX
        '''
        self.content = re.sub(pattern, replacement, self.content, count)

    def replace_assign(self, name, replacement, count = 1):
        '''
        XXX
        '''
        self.sub('\n' + name + ' = .*', '\n' + name + ' = ' + replacement)

    # Determine the pattern to match a version

    _rel_types = '(alpha|beta|candidate|final)'
    match_pat = '\d+\.\d+\.\d+\.' + _rel_types + '\.(\d+|yyyymmdd)'
    match_rel = re.compile(match_pat)

    def replace_version(self, replacement = version_string, count = 1):
        '''
        XXX
        '''
        self.content = self.match_rel.sub(replacement, self.content, count)

    # Determine the release date and the pattern to match a date
    # Mon, 05 Jun 2010 21:17:15 -0700
    # NEW DATE WILL BE INSERTED HERE

    if mode == 'develop':
        new_date = 'NEW DATE WILL BE INSERTED HERE'
    else:
        min = (time.daylight and time.altzone or time.timezone)//60
        hr = min//60
        min = -(min%60 + hr*100)
        new_date =  (time.strftime('%a, %d %b %Y %X', release_date + (0,0,0))
                         + ' %+.4d' % min)

    _days = '(Sun|Mon|Tue|Wed|Thu|Fri|Sat)'
    _months = '(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oce|Nov|Dec)'
    match_date = _days+', \d\d '+_months+' \d\d\d\d \d\d:\d\d:\d\d [+-]\d\d\d\d'
    match_date = re.compile(match_date)

    def replace_date(self, replacement = new_date, count = 1):
        '''
        XXX
        '''
        self.content = self.match_date.sub(replacement, self.content, count)

    def __del__(self):
        '''
        XXX
        '''
        if self.file is not None and self.content != self.orig:
            print('Updating ' + self.file + '...')
            open(self.file, 'w').write(self.content)

if mode == 'post':
    # Set up for the next release series.

    if version_tuple[2]:
        # micro release, increment micro value
        minor = version_tuple[1]
        micro = version_tuple[2] + 1
    else:
        # minor release, increment minor value
        minor = version_tuple[1] + 1
        micro = 0
    new_tuple = (version_tuple[0], minor, micro, 'alpha', 0)
    new_version = '.'.join(map(str, new_tuple[:4])) + '.yyyymmdd'

    # Update ReleaseConfig

    t = UpdateFile('ReleaseConfig')
    if DEBUG: t.file = '/tmp/ReleaseConfig'
    t.replace_assign('version_tuple', str(new_tuple))

    # Update src/CHANGES.txt

    t = UpdateFile(os.path.join('src', 'CHANGES.txt'))
    if DEBUG: t.file = '/tmp/CHANGES.txt'
    t.sub('(\nRELEASE .*)', r"""\nRELEASE  VERSION/DATE TO BE FILLED IN LATER\n
  From John Doe:\n
    - Whatever John Doe did.\n
\1""")

    # Update src/RELEASE.txt

    t = UpdateFile(os.path.join('src', 'RELEASE.txt'),
                   os.path.join('template', 'RELEASE.txt'))
    if DEBUG: t.file = '/tmp/RELEASE.txt'
    t.replace_version(new_version)

    # Update src/Announce.txt

    t = UpdateFile(os.path.join('src', 'Announce.txt'))
    if DEBUG: t.file = '/tmp/Announce.txt'
    t.sub('\nRELEASE .*', '\nRELEASE VERSION/DATE TO BE FILLED IN LATER')
    announce_pattern = """(
  Please note the following important changes scheduled for the next
  release:
)"""
    announce_replace = (r"""\1
    --  FEATURE THAT WILL CHANGE\n
  Please note the following important changes since release """
            + '.'.join(map(str, version_tuple[:3])) + ':\n')
    t.sub(announce_pattern, announce_replace)

    # Write out the last update and exit

    t = None
    sys.exit()

# Update src/CHANGES.txt

t = UpdateFile(os.path.join('src', 'CHANGES.txt'))
if DEBUG: t.file = '/tmp/CHANGES.txt'
t.sub('\nRELEASE .*', '\nRELEASE ' + version_string + ' - ' + t.new_date)

# Update src/RELEASE.txt

t = UpdateFile(os.path.join('src', 'RELEASE.txt'))
if DEBUG: t.file = '/tmp/RELEASE.txt'
t.replace_version()

# Update src/Announce.txt

t = UpdateFile(os.path.join('src', 'Announce.txt'))
if DEBUG: t.file = '/tmp/Announce.txt'
t.sub('\nRELEASE .*', '\nRELEASE ' + version_string + ' - ' + t.new_date)


# Update SConstruct

t = UpdateFile('SConstruct')
if DEBUG: t.file = '/tmp/SConstruct'
t.replace_assign('month_year', repr(month_year))
t.replace_assign('copyright_years', repr(copyright_years))
t.replace_assign('default_version', repr(version_string))

# Update README

t = UpdateFile('README.rst')
if DEBUG: t.file = '/tmp/README.rst'
t.sub('-' + t.match_pat + '\.', '-' + version_string + '.', count = 0)
for suf in ['tar', 'win32', 'zip', 'rpm', 'exe', 'deb']:
    t.sub('-(\d+\.\d+\.\d+)\.%s' % suf,
          '-%s.%s' % (version_string, suf),
          count = 0)

# Update testing/framework/TestSCons.py

t = UpdateFile(os.path.join('testing','framework', 'TestSCons.py'))
if DEBUG: t.file = '/tmp/TestSCons.py'
t.replace_assign('copyright_years', repr(copyright_years))
t.replace_assign('default_version', repr(version_string))
#??? t.replace_assign('SConsVersion', repr(version_string))
t.replace_assign('python_version_unsupported', str(unsupported_version))
t.replace_assign('python_version_deprecated', str(deprecated_version))

# Update Script/Main.py

t = UpdateFile(os.path.join('src', 'engine', 'SCons', 'Script', 'Main.py'))
if DEBUG: t.file = '/tmp/Main.py'
t.replace_assign('unsupported_python_version', str(unsupported_version))
t.replace_assign('deprecated_python_version', str(deprecated_version))

# Update doc/user/main.{in,xml}

docyears = '2004 - %d' % release_date[0]
if os.path.exists(os.path.join('doc', 'user', 'main.in')):
    # this is no longer used as of Dec 2013
    t = UpdateFile(os.path.join('doc', 'user', 'main.in'))
    if DEBUG: t.file = '/tmp/main.in'
    ## TODO debug these
    #t.sub('<pubdate>[^<]*</pubdate>', '<pubdate>' + docyears + '</pubdate>')
    #t.sub('<year>[^<]*</year>', '<year>' + docyears + '</year>')

t = UpdateFile(os.path.join('doc', 'user', 'main.xml'))
if DEBUG: t.file = '/tmp/main.xml'
t.sub('<pubdate>[^<]*</pubdate>', '<pubdate>' + docyears + '</pubdate>')
t.sub('<year>[^<]*</year>', '<year>' + docyears + '</year>')

# Write out the last update

t = None

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
