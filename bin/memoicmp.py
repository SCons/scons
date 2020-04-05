#!/usr/bin/env python
#
# A script to compare the --debug=memoizer output found in
# two different files.

import sys

def memoize_output(fname):
    mout = {}
    #lines=filter(lambda words:
    #             len(words) == 5 and
    #             words[1] == 'hits' and words[3] == 'misses',
    #             map(string.split, open(fname,'r').readlines()))
    #for line in lines:
    #    mout[line[-1]] = ( int(line[0]), int(line[2]) )
    for line in open(fname,'r').readlines():
        words = line.split()
        if len(words) == 5 and words[1] == 'hits' and words[3] == 'misses':
            mout[words[-1]] = ( int(words[0]), int(words[2]) )
    return mout

def memoize_cmp(filea, fileb):
        ma = memoize_output(filea)
        mb = memoize_output(fileb)

        print('All output: %s / %s [delta]'%(filea, fileb))
        print('----------HITS---------- ---------MISSES---------')
        cfmt='%7d/%-7d [%d]'
        ma_o = []
        mb_o = []
        mab  = []
        for k in list(ma.keys()):
                if k in list(mb.keys()):
                        if k not in mab:
                                mab.append(k)
                else:
                        ma_o.append(k)
        for k in list(mb.keys()):
                if k in list(ma.keys()):
                        if k not in mab:
                                mab.append(k)
                else:
                        mb_o.append(k)

        mab.sort()
        ma_o.sort()
        mb_o.sort()

        for k in mab:
                hits = cfmt%(ma[k][0], mb[k][0], mb[k][0]-ma[k][0])
                miss = cfmt%(ma[k][1], mb[k][1], mb[k][1]-ma[k][1])
                print('%-24s %-24s  %s'%(hits, miss, k))

        for k in ma_o:
                hits = '%7d/ --'%(ma[k][0])
                miss = '%7d/ --'%(ma[k][1])
                print('%-24s %-24s  %s'%(hits, miss, k))

        for k in mb_o:
                hits = '    -- /%-7d'%(mb[k][0])
                miss = '    -- /%-7d'%(mb[k][1])
                print('%-24s %-24s  %s'%(hits, miss, k))

        print('-'*(24+24+1+20))


if __name__ == "__main__":
        if len(sys.argv) != 3:
                print("""Usage: %s file1 file2

Compares --debug=memomize output from file1 against file2."""%sys.argv[0])
                sys.exit(1)

        memoize_cmp(sys.argv[1], sys.argv[2])
        sys.exit(0)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
