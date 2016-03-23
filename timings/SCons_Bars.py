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

"""
A quick module for central collection of information about which
Subversion revisions are important for performance implications.
"""

class Bars(dict):
    """
    Dictionary subclass for mapping revision numbers to labels describing
    each revision.

    We provide two extensions:  a .color attribute (for the default
    color) and a .gnuplot() method (for returning a list of revisions
    in the tuple format that scons-time uses to describe vertical bars).
    """
    def __init__(self, dict=None, color=None, **kwargs):
        super(Bars, self).__init__(dict, **kwargs)
        self.color = color
    def gnuplot(self, color=None, labels=False, revs=None):
        if color is None:
            color = self.color
        if revs is None:
            revs = sorted(self.keys())
        if labels:
            result = [ (r, color, None, self[r]) for r in revs ]
        else:
            result = [ (r, color, None, None) for r in revs ]
        return tuple(result)

# The Release_Bars dictionary records the Subversion revisions that
# correspond to each official SCons release.

Release_Bars = Bars(
    color = 7,
    dict = {
        1232 : '0.96.90', 
        1344 : '0.96.91', 
        1435 : '0.96.92', 
        1674 : '0.96.93', 
        1765 : '0.96.94', 
        1835 : '0.96.95', 
        1882 : '0.96.96', 
        1901 : '0.97', 
        2242 : '0.97.0d20070809', 
        2454 : '0.97.0d20070918', 
        2527 : '0.97.0d20071212', 
    },
)


# The Revisions_Bars dictionary records the Subversion revisions that
# correspond to "interesting" changes in timing.  This is essentially the
# global list of interesting changes.  Individual timing configurations
# typically only display bars for a subset of these, the ones that
# actually affect their configuration.
#
# Note that the default behavior of most of the st.conf files is to
# *not* display the labels for each of these lines, since they're long
# and verbose.  So in practice they function as comments describing the
# changes that have timing impacts on various configurations.

Revision_Bars = Bars(
    color = 5,
    dict = {
        1220 : 'Use WeakValueDicts in the Memoizer to reduce memory use.',
        1224 : 'Don\'t create a Node for every file we try to find during scan.',
        1231 : 'Don\'t pick same-named directories in a search path.',
        1241 : 'Optimize out N*M suffix matching in Builder.py.',
        1245 : 'Reduce gen_binfo() time for long source lists.',
        1261 : 'Fix -j re-scanning built files for implicit deps.',
        1262 : 'Match Entries when searching paths for Files or Dirs.',
        1273 : 'Store paths in .sconsign relative to target directory.',
        1282 : 'Cache result from rel_path().',
        1307 : 'Move signature Node tranlation of rel_paths into the class.',
        1346 : 'Give subst logic its own module.',
        1349 : 'More efficient checking for on-disk file entries.',
        1407 : 'Use a Dir scanner instead of a hard-coded method.',
        1433 : 'Remove unnecessary creation of RCS and SCCS Node.Dir nodes.',
        1435 : 'Don\'t convert .sconsign dependencies to Nodes until needed.',
        1468 : 'Use waiting-Node reference counts to speed up Taskmaster.',
        1477 : 'Delay disambiguation of Node.FS.Entry into File/Dir.',
        1533 : 'Fix some disambiguation-delay ramifications.',
        1655 : 'Reduce unnecessary calls to Node.FS.disambiguate().',
        1703 : 'Lobotomize Memoizer.',
        1706 : 'Fix _doLookup value-cache misspellings.',
        1712 : 'PathList, restore caching of Builder source suffixes.',
        1724 : 'Cache Node.FS.find_file() and Node.FS.Dir.srcdir_find_file().',
        1727 : 'Cache Executor methods, reduce calls when scanning.',
        1752 : 'Don\'t cache Builder source suffixes too early.',
        1790 : 'Clean up various module imports (pychecker fixes).',
        1794 : 'Un-fix various later-Python-version pychecker "fixes".',
        1828 : 'Speed up Builder suffix-matching (SuffixMap).',
        2380 : 'The Big Signature Refactoring hits branches/core.',
    },
)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
