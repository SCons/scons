#!/usr/bin/env python
#
# Process a list of Python and/or XML files containing SCons documentation.
#
# Depending on the options, this script creates DocBook-formatted lists
# of the Builders, Tools or construction variables in generated SGML
# files containing the summary text and/or .mod files contining the
# ENTITY definitions for each item.
#
import getopt
import os.path
import re
import string
import StringIO
import sys
import xml.sax

import SConsDoc

base_sys_path = [os.getcwd() + '/build/test-tar-gz/lib/scons'] + sys.path

helpstr = """\
Usage: scons-varlist.py [-b .gen,.mod] [-t .gen,.mod] [-v .gen,.mod] [infile]
Options:
  -m, --modfile               .mod file to hold Builder entities
"""

opts, args = getopt.getopt(sys.argv[1:],
                           "b:t:v:",
                           ['builders=', 'tools=', 'variables='])

buildersfiles = None
toolsfiles = None
variablesfiles = None

for o, a in opts:
    if o == '-b' or o == '--builders':
        buildersfiles = a
    elif o == '-t' or o == '--tools':
        toolsfiles = a
    elif o == '-v' or o == '--variables':
        variablesfiles = a

h = SConsDoc.SConsDocHandler()
saxparser = xml.sax.make_parser()
saxparser.setContentHandler(h)
saxparser.setErrorHandler(h)

preamble = """\
<?xml version="1.0"?>
<scons_doc>
"""

postamble = """\
</scons_doc>
"""

for f in args:
    _, ext = os.path.splitext(f)
    if ext == '.py':
        dir, _ = os.path.split(f)
        if dir:
            sys.path = [dir] + base_sys_path
        module = SConsDoc.importfile(f)
        h.set_file_info(f, len(preamble.split('\n')))
        try:
            content = module.__scons_doc__
        except AttributeError:
            content = None
        else:
            del module.__scons_doc__
    else:
        h.set_file_info(f, len(preamble.split('\n')))
        content = open(f).read()
    if content:
        content = content.replace('&', '&amp;')
        input = preamble + content + postamble
        try:
            saxparser.parse(StringIO.StringIO(input))
        except:
            sys.stderr.write("error in %s\n" % f)
            raise

Warning = """\
<!--
THIS IS AN AUTOMATICALLY-GENERATED FILE.  DO NOT EDIT.
-->
"""

Regular_Entities_Header = """\
<!--

  Regular %s entities.

-->
"""

Link_Entities_Header = """\
<!--

  Entities that are links to the %s entries in the appendix.

-->
"""

class XXX:
    def __init__(self, entries, **kw):
        values = entries.values()
        values.sort()
        self.values = values
        for k, v in kw.items():
            setattr(self, k, v)
    def write_gen(self, filename):
        if not filename:
            return
        f = open(filename, 'w')
        for v in self.values:
            f.write('\n<varlistentry id="%s%s">\n' %
                        (self.prefix, self.idfunc(v.name)))
            for term in self.termfunc(v.name):
                f.write('<term><%s>%s</%s></term>\n' %
                        (self.tag, term, self.tag))
            f.write('<listitem>\n')
            for chunk in v.summary.body:
                f.write(str(chunk))
            #if v.uses:
            #    u = map(lambda x, s: '&%slink-%s;' % (s.prefix, x), v.uses)
            #    f.write('<para>\n')
            #    f.write('Uses:  ' + ', '.join(u) + '.\n')
            #    f.write('</para>\n')
            f.write('</listitem>\n')
            f.write('</varlistentry>\n')
    def write_mod(self, filename):
        if not filename:
            return
        f = open(filename, 'w')
        f.write(Warning)
        f.write('\n')
        f.write(Regular_Entities_Header % self.description)
        f.write('\n')
        for v in self.values:
            f.write('<!ENTITY %s%s "<%s>%s</%s>">\n' %
                        (self.prefix, self.idfunc(v.name),
                         self.tag, self.entityfunc(v.name), self.tag))
        f.write('\n')
        f.write(Warning)
        f.write('\n')
        f.write(Link_Entities_Header % self.description)
        f.write('\n')
        for v in self.values:
            f.write('<!ENTITY %slink-%s \'<link linkend="%s%s"><%s>%s</%s></link>\'>\n' %
                        (self.prefix, self.idfunc(v.name),
                         self.prefix, self.idfunc(v.name),
                         self.tag, self.entityfunc(v.name), self.tag))
        f.write('\n')
        f.write(Warning)

if buildersfiles:
    g = XXX(h.builders,
            description = 'builder',
            prefix = 'b-',
            tag = 'function',
            idfunc = lambda x: x,
            termfunc = lambda x: [x+'()', 'env.'+x+'()'],
            entityfunc = lambda x: x)

    gen, mod = string.split(buildersfiles, ',')
    g.write_gen(gen)
    g.write_mod(mod)

if toolsfiles:
    g = XXX(h.tools,
            description = 'tool',
            prefix = 't-',
            tag = 'literal',
            idfunc = lambda x: string.replace(x, '+', 'X'),
            termfunc = lambda x: [x],
            entityfunc = lambda x: x)

    gen, mod = string.split(toolsfiles, ',')
    g.write_gen(gen)
    g.write_mod(mod)

if variablesfiles:
    g = XXX(h.cvars,
            description = 'construction variable',
            prefix = 'cv-',
            tag = 'envar',
            idfunc = lambda x: x,
            termfunc = lambda x: [x],
            entityfunc = lambda x: '$'+x)

    gen, mod = string.split(variablesfiles, ',')
    g.write_gen(gen)
    g.write_mod(mod)
