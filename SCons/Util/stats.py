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
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
This package provides a way to gather various statistics during a SCons run and dump that info in several formats

Additionally, it probably makes sense to do stderr/stdout output of those statistics here as well

There are basically two types of stats.
1. Timer (start/stop/time) for specific event.  These events can be hierarchical. So you can record the children events of some parent.
   Think program compile could contain the total Program builder time, which could include linking, and stripping the executable
2. Counter. Counting the number of events and/or objects created. This would likely only be reported at the end of a given SCons run,
   though it might be useful to query during a run.

"""
import json

import SCons.Debug

ALL_STATS = {}
ENABLE_JSON = False


def AddStatType(name, stat_object):
    """
    Add a statistic type to the global collection
    """
    if name in ALL_STATS:
        raise UserWarning(f'Stat type {name} already exists')
    else:
        ALL_STATS[name] = stat_object


# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
class Stats:
    def __init__(self):
        self.stats = []
        self.labels = []
        self.append = self.do_nothing
        self.print_stats = self.do_nothing
        self.enabled = False

    def do_append(self, label):
        raise NotImplementedError

    def do_print(self):
        raise NotImplementedError

    def enable(self, outfp):
        self.outfp = outfp
        self.append = self.do_append
        self.print_stats = self.do_print
        self.enabled = True

    def do_nothing(self, *args, **kw):
        pass


class CountStats(Stats):

    def __init__(self):
        super().__init__()
        self.stats_table = {}

    def do_append(self, label):
        self.labels.append(label)
        self.stats.append(SCons.Debug.fetchLoggedInstances())

    def do_print(self):
        self.stats_table = {}
        for s in self.stats:
            for n in [t[0] for t in s]:
                self.stats_table[n] = [0, 0, 0, 0]
        i = 0
        for s in self.stats:
            for n, c in s:
                self.stats_table[n][i] = c
            i = i + 1
        self.outfp.write("Object counts:\n")
        pre = ["   "]
        post = ["   %s\n"]
        l = len(self.stats)
        fmt1 = ''.join(pre + [' %7s'] * l + post)
        fmt2 = ''.join(pre + [' %7d'] * l + post)
        labels = self.labels[:l]
        labels.append(("", "Class"))
        self.outfp.write(fmt1 % tuple([x[0] for x in labels]))
        self.outfp.write(fmt1 % tuple([x[1] for x in labels]))
        for k in sorted(self.stats_table.keys()):
            r = self.stats_table[k][:l] + [k]
            self.outfp.write(fmt2 % tuple(r))


class MemStats(Stats):
    def do_append(self, label):
        self.labels.append(label)
        self.stats.append(SCons.Debug.memory())

    def do_print(self):
        fmt = 'Memory %-32s %12d\n'
        for label, stats in zip(self.labels, self.stats):
            self.outfp.write(fmt % (label, stats))


COUNT_STATS = CountStats()
MEMORY_STATS = MemStats()


def WriteJsonFile():
    """

    """
    print("DUMPING JSON FILE")
    json_structure = {}
    if COUNT_STATS.enabled:
        json_structure['Object counts'] = {}

        oc = json_structure['Object counts']
        for c in COUNT_STATS.stats_table:
            oc[c] = {}
            for l, v in zip(COUNT_STATS.labels, COUNT_STATS.stats_table[c]):
                oc[c][''.join(l)] = v

    if MEMORY_STATS.enabled:
        json_structure['Memory'] = {}

        m = json_structure['Memory']
        for label, stats in zip(MEMORY_STATS.labels, MEMORY_STATS.stats):
            m[label] =stats

    with open("scons_stats.json", 'w') as sf:
        sf.write(json.dumps(json_structure))
