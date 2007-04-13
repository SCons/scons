#!/usr/bin/env python
#
# Process a list of Python and/or XML files containing SCons documentation.
#
# This script creates formatted lists of the Builders, Tools or
# construction variables documented in the specified XML files.
#
# Dependening on the options, the lists are output in either
# DocBook-formatted generated SGML files containing the summary text
# and/or .mod files contining the ENTITY definitions for each item,
# or in man-page-formatted output.
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
Usage: scons-proc.py [--man|--sgml] \
                        [-b file(s)] [-t file(s)] [-v file(s)] [infile ...]
Options:
  -b file(s)        dump builder information to the specified file(s)
  -t file(s)        dump tool information to the specified file(s)
  -v file(s)        dump variable information to the specified file(s)
  --man             print info in man page format, each -[btv] argument
                    is a single file name
  --sgml            (default) print info in SGML format, each -[btv] argument
                    is a pair of comma-separated .gen,.mod file names
"""

opts, args = getopt.getopt(sys.argv[1:],
                           "b:t:v:",
                           ['builders=', 'man', 'sgml', 'tools=', 'variables='])

buildersfiles = None
output_type = '--sgml'
toolsfiles = None
variablesfiles = None

for o, a in opts:
    if o in ['-b', '--builders']:
        buildersfiles = a
    elif o in ['--man', '--sgml']:
        output_type = o
    elif o in ['-t', '--tools']:
        toolsfiles = a
    elif o in ['-v', '--variables']:
        variablesfiles = a

h = SConsDoc.SConsDocHandler()
saxparser = xml.sax.make_parser()
saxparser.setContentHandler(h)
saxparser.setErrorHandler(h)

xml_preamble = """\
<?xml version="1.0"?>
<scons_doc>
"""

xml_postamble = """\
</scons_doc>
"""

for f in args:
    _, ext = os.path.splitext(f)
    if ext == '.py':
        dir, _ = os.path.split(f)
        if dir:
            sys.path = [dir] + base_sys_path
        module = SConsDoc.importfile(f)
        h.set_file_info(f, len(xml_preamble.split('\n')))
        try:
            content = module.__scons_doc__
        except AttributeError:
            content = None
        else:
            del module.__scons_doc__
    else:
        h.set_file_info(f, len(xml_preamble.split('\n')))
        content = open(f).read()
    if content:
        content = content.replace('&', '&amp;')
        input = xml_preamble + content + xml_postamble
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

class SCons_XML:
    def __init__(self, entries, **kw):
        values = entries.values()
        values.sort()
        self.values = values
        for k, v in kw.items():
            setattr(self, k, v)
    def fopen(self, name):
        if name == '-':
            return sys.stdout
        return open(name, 'w')

class SCons_XML_to_SGML(SCons_XML):
    def write(self, files):
        gen, mod = string.split(files, ',')
        g.write_gen(gen)
        g.write_mod(mod)
    def write_gen(self, filename):
        if not filename:
            return
        f = self.fopen(filename)
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
        f = self.fopen(filename)
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

class SCons_XML_to_man(SCons_XML):
    def mansep(self):
        return ['\n']
    def initial_chunks(self, name):
        return [name]
    def write(self, filename):
        if not filename:
            return
        f = self.fopen(filename)
        chunks = []
        for v in self.values:
            chunks.extend(self.mansep())
            for n in self.initial_chunks(v.name):
                chunks.append('.IP %s\n' % n)
            chunks.extend(map(str, v.summary.body))

        body = ''.join(chunks)
        body = string.replace(body, '<programlisting>', '.ES')
        body = string.replace(body, '</programlisting>', '.EE')
        body = string.replace(body, '\n</para>\n<para>\n', '\n\n')
        body = string.replace(body, '<para>\n', '')
        body = string.replace(body, '<para>', '\n')
        body = string.replace(body, '</para>\n', '')
        body = re.sub('\.EE\n\n+(?!\.IP)', '.EE\n.IP\n', body)
        body = re.sub('&(scons|SConstruct|SConscript|jar);', r'\\fB\1\\fP', body)
        body = string.replace(body, '&Dir;', r'\fBDir\fP')
        body = re.sub('&b(-link)?-([^;]*);', r'\\fB\2\\fP()', body)
        body = re.sub('&cv(-link)?-([^;]*);', r'$\2', body)
        body = re.sub(r'<(command|envar|filename|literal|option)>([^<]*)</\1>',
                      r'\\fB\2\\fP', body)
        body = re.sub(r'<(classname|emphasis|varname)>([^<]*)</\1>',
                      r'\\fI\2\\fP', body)
        body = re.compile(r'^\\f([BI])(.*)\\fP\s*$', re.M).sub(r'.\1 \2', body)
        body = re.compile(r'^\\f([BI])(.*)\\fP(\S+)', re.M).sub(r'.\1R \2 \3', body)
        body = string.replace(body, '&lt;', '<')
        body = string.replace(body, '&gt;', '>')
        body = re.sub(r'\\([^f])', r'\\\\\1', body)
        body = re.compile("^'\\\\\\\\", re.M).sub("'\\\\", body)
        body = re.compile(r'^\.([BI]R?) -', re.M).sub(r'.\1 \-', body)
        body = re.compile(r'^\.([BI]R?) (\S+)\\\\(\S+)', re.M).sub(r'.\1 "\2\\\\\\\\\2"', body)
        body = re.compile(r'\\f([BI])-', re.M).sub(r'\\f\1\-', body)
        f.write(body)

if output_type == '--man':
    processor_class = SCons_XML_to_man
elif output_type == '--sgml':
    processor_class = SCons_XML_to_SGML
else:
    sys.stderr.write("Unknown output type '%s'\n" % output_type)
    sys.exit(1)

if buildersfiles:
    g = processor_class(h.builders,
            description = 'builder',
            prefix = 'b-',
            tag = 'function',
            idfunc = lambda x: x,
            termfunc = lambda x: [x+'()', 'env.'+x+'()'],
            entityfunc = lambda x: x)

    g.mansep = lambda: ['\n', "'\\" + '"'*69 + '\n']
    g.initial_chunks = lambda n: [n+'()', 'env.'+n+'()']

    g.write(buildersfiles)

if toolsfiles:
    g = processor_class(h.tools,
            description = 'tool',
            prefix = 't-',
            tag = 'literal',
            idfunc = lambda x: string.replace(x, '+', 'X'),
            termfunc = lambda x: [x],
            entityfunc = lambda x: x)

    g.write(toolsfiles)

if variablesfiles:
    g = processor_class(h.cvars,
            description = 'construction variable',
            prefix = 'cv-',
            tag = 'envar',
            idfunc = lambda x: x,
            termfunc = lambda x: [x],
            entityfunc = lambda x: '$'+x)

    g.write(variablesfiles)
