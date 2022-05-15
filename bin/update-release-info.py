#!/usr/bin/env python
"""
This program takes information about a release in the ReleaseConfig file
and inserts the information in various files.  It helps to keep the files
in sync because it never forgets which files need to be updated, nor what
information should be inserted in each file.

It takes one parameter that says what the mode of update should be, which
may be one of 'develop', 'release', or 'post'.

In 'develop' mode, which is what someone would use as part of their own
development practices, the release type is forced to be 'dev' and the
patch level is the string 'yyyymmdd'.  Otherwise, it's the same as the
'release' mode.

In 'release' mode, the release type is taken from ReleaseConfig and the
patch level is calculated from the release date for non-final runs and
taken from the version tuple for final runs.  It then inserts information
in various files:
  - The RELEASE header line in src/CHANGES.txt and src/Announce.txt.
  - The version string at the top of src/RELEASE.txt.
  - The version string in the 'default_version' variable in testing/framework/TestSCons.py.
  - The copyright years in testing/framework/TestSCons.py.
  - The unsupported and deprecated Python floors in testing/framework/TestSCons.py
    and src/engine/SCons/Script/Main.py
  - The version string in the filenames in README.

In 'post' mode, files are prepared for the next release cycle:
  - In ReleaseConfig, the version tuple is updated for the next release
    by incrementing the release number (either minor or micro, depending
    on the branch) and resetting release type to 'dev'.
  - A blank template replaces src/RELEASE.txt.
  - A new section to accumulate changes is added to src/CHANGES.txt and
    src/Announce.txt.
"""
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
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE


import argparse
import os
import re
import sys
import time

DEBUG = os.environ.get('DEBUG', 0)


class ReleaseInfo:
    def __init__(self, args):
        self.config = {}
        self.args = args
        self.release_date = time.localtime()[:6]

        self.unsupported_version = None
        self.deprecated_version = None

        # version_tuple = (3, 1, 3, 'alpha', 0)
        self.version_tuple = (-1, -1, -1, 'not_set', -1)

        self.version_string = "UNSET"
        self.version_type = 'UNSET'
        self.month_year = 'UNSET'
        self.copyright_years = 'UNSET'
        self.new_date = 'NEW DATE WILL BE INSERTED HERE'

        self.read_config()
        self.process_config()
        if not self.args.timestamp:
            self.set_new_date()

    def read_config(self):
        # Get configuration information

        config = dict()
        with open('ReleaseConfig') as f:
            release_config = f.read()
        exec(release_config, globals(), config)

        self.config = config

    def process_config(self):
        """
        Process and validate the config info loaded from ReleaseConfig file
        """

        try:
            self.version_tuple = self.config['version_tuple']
            self.unsupported_version = self.config['unsupported_python_version']
            self.deprecated_version = self.config['deprecated_python_version']
        except KeyError:
            print('''ERROR: Config file must contain at least version_tuple,
\tunsupported_python_version, and deprecated_python_version.''')
            sys.exit(1)

        if 'release_date' in self.config:
            self.release_date = self.config['release_date']
            if len(self.release_date) == 3:
                self.release_date = self.release_date + time.localtime()[3:6]
            if len(self.release_date) != 6:
                print('''ERROR: Invalid release date''', self.release_date)
                sys.exit(1)

        yyyy, mm, dd, h, m, s = self.release_date
        date_string = "".join(["%.2d" % d for d in self.release_date])

        if self.args.timestamp:
            date_string = self.args.timestamp

        if self.args.mode == 'develop' and self.version_tuple[3] != 'a':
            self.version_tuple == self.version_tuple[:3] + ('a', 0)

        if len(self.version_tuple) > 3 and self.version_tuple[3] != 'final':
            self.version_tuple = self.version_tuple[:4] + (date_string,)

        self.version_string = '.'.join(map(str, self.version_tuple[:4])) + date_string

        if len(self.version_tuple) > 3:
            self.version_type = self.version_tuple[3]
        else:
            self.version_type = 'final'

        if self.version_type not in ['a', 'b', 'rc', 'final']:
            print(("""ERROR: `%s' is not a valid release type in version tuple;
\tit must be one of a, b, rc, or final""" % self.version_type))
            sys.exit(1)

        try:
            self.month_year = self.config['month_year']
        except KeyError:
            if self.args.timestamp:
                self.month_year = "MONTH YEAR"
            else:
                self.month_year = time.strftime('%B %Y', self.release_date + (0, 0, 0))

        try:
            self.copyright_years = self.config['copyright_years']
        except KeyError:
            self.copyright_years = '2001 - %d' % (self.release_date[0] + 1)

        if DEBUG:
            print('version tuple', self.version_tuple)
            print('unsupported Python version', self.unsupported_version)
            print('deprecated Python version', self.deprecated_version)
            print('release date', self.release_date)
            print('version string', self.version_string)
            print('month year', self.month_year)
            print('copyright years', self.copyright_years)

    def set_new_date(self):
        """
        Determine the release date and the pattern to match a date
        Mon, 05 Jun 2010 21:17:15 -0700
        NEW DATE WILL BE INSERTED HERE
        """
        min = (time.daylight and time.altzone or time.timezone) // 60
        hr = min // 60
        min = -(min % 60 + hr * 100)
        self.new_date = (time.strftime('%a, %d %b %Y %X', self.release_date + (0, 0, 0))
                         + ' %+.4d' % min)


class UpdateFile:
    """ XXX """

    rel_info = None
    mode = 'develop'
    _days = r'(Sun|Mon|Tue|Wed|Thu|Fri|Sat)'
    _months = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oce|Nov|Dec)'
    match_date = r''.join([_days, r', \d\d ', _months, r' \d\d\d\d \d\d:\d\d:\d\d [+-]\d\d\d\d'])
    match_date = re.compile(match_date)

    # Determine the pattern to match a version

    _rel_types = r'[(a|b|rc)]'
    match_pat = r'\d+\.\d+\.\d+\.' + _rel_types + r'\.?(\d+|yyyymmdd)'
    match_rel = re.compile(match_pat)

    def __init__(self, file, orig=None):
        if orig is None:
            orig = file

        try:
            with open(orig, 'r') as f:
                self.content = f.read()
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

    def sub(self, pattern, replacement, count=1):
        """ XXX """
        self.content = re.sub(pattern, replacement, self.content, count)

    def replace_assign(self, name, replacement, count=1):
        """ XXX """
        self.sub('\n' + name + ' = .*', '\n' + name + ' = ' + replacement)

    def replace_version(self, count=1):
        """ XXX """
        self.content = self.match_rel.sub(rel_info.version_string, self.content, count)

    def replace_date(self, count=1):
        """ XXX """
        self.content = self.match_date.sub(rel_info.new_date, self.content, count)

    def __del__(self):
        """ XXX """
        if self.file is not None and self.content != self.orig:
            print('Updating ' + self.file + '...')
            with open(self.file, 'w') as f:
                f.write(self.content)


def main(args, rel_info):
    if args.mode == 'post':
        # Set up for the next release series.

        if rel_info.version_tuple[2]:
            # micro release, increment micro value
            minor = rel_info.version_tuple[1]
            micro = rel_info.version_tuple[2] + 1
        else:
            # minor release, increment minor value
            minor = rel_info.version_tuple[1] + 1
            micro = 0
        new_tuple = (rel_info.version_tuple[0], minor, micro, 'a', 0)
        new_version = '.'.join(map(str, new_tuple[:3])) + new_tuple[3] + 'yyyymmdd'

        rel_info.version_string = new_version

        # Update ReleaseConfig
        t = UpdateFile('ReleaseConfig')
        if DEBUG:
            t.file = '/tmp/ReleaseConfig'
        t.replace_assign('version_tuple', str(new_tuple))

        # Update src/CHANGES.txt
        t = UpdateFile('CHANGES.txt')
        if DEBUG:
            t.file = '/tmp/CHANGES.txt'
        t.sub('(\nRELEASE .*)', r"""\nRELEASE  VERSION/DATE TO BE FILLED IN LATER\n
      From John Doe:\n
        - Whatever John Doe did.\n\n\1""")

        # Update src/RELEASE.txt
        t = UpdateFile('RELEASE.txt',
                       os.path.join('template', 'RELEASE.txt'))
        if DEBUG:
            t.file = '/tmp/RELEASE.txt'
        t.replace_version()

        # Update README
        for readme_file in ['README.rst', 'README-SF.rst']:
            t = UpdateFile(readme_file)
            if DEBUG: t.file = os.path.join('/tmp/', readme_file)
            t.sub('-' + t.match_pat + r'\.', '-' + rel_info.version_string + '.', count=0)
            for suf in ['tar', 'win32', 'zip']:
                t.sub(r'-(\d+\.\d+\.\d+)\.%s' % suf,
                      '-%s.%s' % (rel_info.version_string, suf),
                      count=0)

        # Update testing/framework/TestSCons.py
        t = UpdateFile(os.path.join('testing', 'framework', 'TestSCons.py'))
        if DEBUG:
            t.file = '/tmp/TestSCons.py'
        t.replace_assign('copyright_years', repr(rel_info.copyright_years))
        t.replace_assign('default_version', repr(rel_info.version_string))
        # ??? t.replace_assign('SConsVersion', repr(version_string))
        t.replace_assign('python_version_unsupported', str(rel_info.unsupported_version))
        t.replace_assign('python_version_deprecated', str(rel_info.deprecated_version))

        # Update Script/Main.py
        t = UpdateFile(os.path.join('SCons', 'Script', 'Main.py'))
        if DEBUG:
            t.file = '/tmp/Main.py'
        t.replace_assign('unsupported_python_version', str(rel_info.unsupported_version))
        t.replace_assign('deprecated_python_version', str(rel_info.deprecated_version))

        # Update doc/user/main.xml
        docyears = '2004 - %d' % rel_info.release_date[0]
        t = UpdateFile(os.path.join('doc', 'user', 'main.xml'))
        if DEBUG:
            t.file = '/tmp/main.xml'
        t.sub('<pubdate>[^<]*</pubdate>', '<pubdate>Released: ' + rel_info.new_date + '</pubdate>')
        t.sub('<year>[^<]*</year>', '<year>' + docyears + '</year>')

        # Write out the last update

        t = None


def parse_arguments():
    """
    Create ArgumentParser object and process arguments
    """

    parser = argparse.ArgumentParser(prog='update-release-info.py')
    parser.add_argument('mode', nargs='?', choices=['develop', 'release', 'post'], default='post')
    parser.add_argument('--verbose', dest='verbose', action='store_true', help='Enable verbose logging')

    parser.add_argument('--timestamp', dest='timestamp', help='Override the default current timestamp')

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    options = parse_arguments()
    rel_info = ReleaseInfo(options)
    UpdateFile.rel_info = rel_info
    main(options, rel_info)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
