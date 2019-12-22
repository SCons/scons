import os.path
import re

from SCons.Script import Builder, Action, Scanner

def soelim(target, source, env):
    """
    Interpolate files included in [gnt]roff source files using the
    .so directive.

    This behaves somewhat like the soelim(1) wrapper around groff, but
    makes us independent of whether the actual underlying implementation
    includes an soelim() command or the corresponding command-line option
    to groff(1).  The key behavioral difference is that this doesn't
    recursively include .so files from the include file.  Not yet, anyway.
    """
    t = str(target[0])
    s = str(source[0])
    dir, f = os.path.split(s)
    with open(t, 'w') as tfp, open(s, 'r') as sfp:
        for line in sfp.readlines():
            if line[:4] in ['.so ', "'so "]:
                sofile = os.path.join(dir, line[4:-1])
                with open(sofile, 'r') as f:
                    tfp.write(f.read())
            else:
                tfp.write(line)

def soscan(node, env, path):
    c = node.get_text_contents()
    return re.compile(r"^[.']so\s+(\S+)", re.M).findall(c)

soelimbuilder = Builder(action = Action(soelim),
                        source_scanner = Scanner(soscan))
