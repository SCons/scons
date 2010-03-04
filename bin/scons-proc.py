#!/usr/bin/env python
#
# Process a list of Python and/or XML files containing SCons documentation.
#
# This script creates formatted lists of the Builders, functions, Tools
# or construction variables documented in the specified XML files.
#
# Dependening on the options, the lists are output in either
# DocBook-formatted generated XML files containing the summary text
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
Usage: scons-proc.py [--man|--xml]
                     [-b file(s)] [-f file(s)] [-t file(s)] [-v file(s)]
                     [infile ...]
Options:
  -b file(s)        dump builder information to the specified file(s)
  -f file(s)        dump function information to the specified file(s)
  -t file(s)        dump tool information to the specified file(s)
  -v file(s)        dump variable information to the specified file(s)
  --man             print info in man page format, each -[btv] argument
                    is a single file name
  --xml             (default) print info in SML format, each -[btv] argument
                    is a pair of comma-separated .gen,.mod file names
"""

opts, args = getopt.getopt(sys.argv[1:],
                           "b:f:ht:v:",
                           ['builders=', 'help',
                            'man', 'xml', 'tools=', 'variables='])

buildersfiles = None
functionsfiles = None
output_type = '--xml'
toolsfiles = None
variablesfiles = None

for o, a in opts:
    if o in ['-b', '--builders']:
        buildersfiles = a
    elif o in ['-f', '--functions']:
        functionsfiles = a
    elif o in ['-h', '--help']:
        sys.stdout.write(helpstr)
        sys.exit(0)
    elif o in ['--man', '--xml']:
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
        self.values = entries
        for k, v in kw.items():
            setattr(self, k, v)
    def fopen(self, name):
        if name == '-':
            return sys.stdout
        return open(name, 'w')

class SCons_XML_to_XML(SCons_XML):
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
                        (v.prefix, v.idfunc()))
            for term in v.termfunc():
                f.write('<term><%s>%s</%s></term>\n' %
                        (v.tag, term, v.tag))
            f.write('<listitem>\n')
            for chunk in v.summary.body:
                f.write(str(chunk))
            if v.sets:
                s = map(lambda x: '&cv-link-%s;' % x, v.sets)
                f.write('<para>\n')
                f.write('Sets:  ' + ', '.join(s) + '.\n')
                f.write('</para>\n')
            if v.uses:
                u = map(lambda x: '&cv-link-%s;' % x, v.uses)
                f.write('<para>\n')
                f.write('Uses:  ' + ', '.join(u) + '.\n')
                f.write('</para>\n')
            f.write('</listitem>\n')
            f.write('</varlistentry>\n')
    def write_mod(self, filename):
        description = self.values[0].description
        if not filename:
            return
        f = self.fopen(filename)
        f.write(Warning)
        f.write('\n')
        f.write(Regular_Entities_Header % description)
        f.write('\n')
        for v in self.values:
            f.write('<!ENTITY %s%s "<%s>%s</%s>">\n' %
                        (v.prefix, v.idfunc(),
                         v.tag, v.entityfunc(), v.tag))
        f.write('\n')
        f.write(Warning)
        f.write('\n')
        f.write(Link_Entities_Header % description)
        f.write('\n')
        for v in self.values:
            f.write('<!ENTITY %slink-%s \'<link linkend="%s%s"><%s>%s</%s></link>\'>\n' %
                        (v.prefix, v.idfunc(),
                         v.prefix, v.idfunc(),
                         v.tag, v.entityfunc(), v.tag))
        f.write('\n')
        f.write(Warning)

class SCons_XML_to_man(SCons_XML):
    def write(self, filename):
        if not filename:
            return
        f = self.fopen(filename)
        chunks = []
        for v in self.values:
            chunks.extend(v.mansep())
            chunks.extend(v.initial_chunks())
            chunks.extend(map(str, v.summary.body))

        body = ''.join(chunks)
        body = string.replace(body, '<programlisting>', '.ES')
        body = string.replace(body, '</programlisting>', '.EE')
        body = string.replace(body, '\n</para>\n<para>\n', '\n\n')
        body = string.replace(body, '<para>\n', '')
        body = string.replace(body, '<para>', '\n')
        body = string.replace(body, '</para>\n', '')

        body = string.replace(body, '<variablelist>\n', '.RS 10\n')
        body = re.compile(r'<varlistentry>\n<term>([^<]*)</term>\n<listitem>\n').sub(r'.HP 6\n.B \1\n', body)
        body = string.replace(body, '</listitem>\n', '')
        body = string.replace(body, '</varlistentry>\n', '')
        body = string.replace(body, '</variablelist>\n', '.RE\n')

        body = re.sub(r'\.EE\n\n+(?!\.IP)', '.EE\n.IP\n', body)
        body = string.replace(body, '\n.IP\n\'\\"', '\n\n\'\\"')
        body = re.sub('&(scons|SConstruct|SConscript|jar);', r'\\fB\1\\fP', body)
        body = string.replace(body, '&Dir;', r'\fBDir\fP')
        body = string.replace(body, '&target;', r'\fItarget\fP')
        body = string.replace(body, '&source;', r'\fIsource\fP')
        body = re.sub('&b(-link)?-([^;]*);', r'\\fB\2\\fP()', body)
        body = re.sub('&cv(-link)?-([^;]*);', r'$\2', body)
        body = re.sub('&f(-link)?-([^;]*);', r'\\fB\2\\fP()', body)
        body = re.sub(r'<(command|envar|filename|function|literal|option)>([^<]*)</\1>',
                      r'\\fB\2\\fP', body)
        body = re.sub(r'<(classname|emphasis|varname)>([^<]*)</\1>',
                      r'\\fI\2\\fP', body)
        body = re.compile(r'^\\f([BI])([^\\]* [^\\]*)\\fP\s*$', re.M).sub(r'.\1 "\2"', body)
        body = re.compile(r'^\\f([BI])(.*)\\fP\s*$', re.M).sub(r'.\1 \2', body)
        body = re.compile(r'^\\f([BI])(.*)\\fP(\S+)$', re.M).sub(r'.\1R \2 \3', body)
        body = re.compile(r'^(\S+)\\f([BI])(.*)\\fP$', re.M).sub(r'.R\2 \1 \3', body)
        body = string.replace(body, '&lt;', '<')
        body = string.replace(body, '&gt;', '>')
        body = re.sub(r'\\([^f])', r'\\\\\1', body)
        body = re.compile("^'\\\\\\\\", re.M).sub("'\\\\", body)
        body = re.compile(r'^\.([BI]R?) --', re.M).sub(r'.\1 \-\-', body)
        body = re.compile(r'^\.([BI]R?) -', re.M).sub(r'.\1 \-', body)
        body = re.compile(r'^\.([BI]R?) (\S+)\\\\(\S+)$', re.M).sub(r'.\1 "\2\\\\\\\\\2"', body)
        body = re.compile(r'\\f([BI])-', re.M).sub(r'\\f\1\-', body)
        f.write(body)

class Proxy:
    def __init__(self, subject):
        """Wrap an object as a Proxy object"""
        self.__subject = subject

    def __getattr__(self, name):
        """Retrieve an attribute from the wrapped object.  If the named
           attribute doesn't exist, AttributeError is raised"""
        return getattr(self.__subject, name)

    def get(self):
        """Retrieve the entire wrapped object"""
        return self.__subject

    def __cmp__(self, other):
        if issubclass(other.__class__, self.__subject.__class__):
            return cmp(self.__subject, other)
        return cmp(self.__dict__, other.__dict__)

class Builder(Proxy):
    description = 'builder'
    prefix = 'b-'
    tag = 'function'
    def idfunc(self):
        return self.name
    def termfunc(self):
        return ['%s()' % self.name, 'env.%s()' % self.name]
    def entityfunc(self):
        return self.name
    def mansep(self):
        return ['\n', "'\\" + '"'*69 + '\n']
    def initial_chunks(self):
        return [ '.IP %s\n' % t for t in self.termfunc() ]

class Function(Proxy):
    description = 'function'
    prefix = 'f-'
    tag = 'function'
    def idfunc(self):
        return self.name
    def termfunc(self):
        return ['%s()' % self.name, 'env.%s()' % self.name]
    def entityfunc(self):
        return self.name
    def mansep(self):
        return ['\n', "'\\" + '"'*69 + '\n']
    def initial_chunks(self):
        try:
            x = self.arguments
        except AttributeError:
            x = '()'
        result = []
        if self.global_signature != "0":
            result.append('.TP\n.RI %s%s\n' % (self.name, x))
        if self.env_signature != "0":
            result.append('.TP\n.IR env .%s%s\n' % (self.name, x))
        return result

class Tool(Proxy):
    description = 'tool'
    prefix = 't-'
    tag = 'literal'
    def idfunc(self):
        return string.replace(self.name, '+', 'X')
    def termfunc(self):
        return [self.name]
    def entityfunc(self):
        return self.name
    def mansep(self):
        return ['\n']
    def initial_chunks(self):
        return ['.IP %s\n' % self.name]

class Variable(Proxy):
    description = 'construction variable'
    prefix = 'cv-'
    tag = 'envar'
    def idfunc(self):
        return self.name
    def termfunc(self):
        return [self.name]
    def entityfunc(self):
        return '$' + self.name
    def mansep(self):
        return ['\n']
    def initial_chunks(self):
        return ['.IP %s\n' % self.name]

if output_type == '--man':
    processor_class = SCons_XML_to_man
elif output_type == '--xml':
    processor_class = SCons_XML_to_XML
else:
    sys.stderr.write("Unknown output type '%s'\n" % output_type)
    sys.exit(1)

if buildersfiles:
    g = processor_class([ Builder(b) for b in sorted(h.builders.values()) ])
    g.write(buildersfiles)

if functionsfiles:
    g = processor_class([ Function(b) for b in sorted(h.functions.values()) ])
    g.write(functionsfiles)

if toolsfiles:
    g = processor_class([ Tool(t) for t in sorted(h.tools.values()) ])
    g.write(toolsfiles)

if variablesfiles:
    g = processor_class([ Variable(v) for v in sorted(h.cvars.values()) ])
    g.write(variablesfiles)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
