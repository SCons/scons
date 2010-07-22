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
import os
import re
import string
import sys
import xml.sax
try:
    from io import StringIO
except ImportError:
    # No 'io' module or no StringIO in io
    exec('from cStringIO import StringIO')

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
        # Strip newlines after comments so they don't turn into
        # spurious paragraph separators.
        content = content.replace('-->\n', '-->')
        input = xml_preamble + content + xml_postamble
        try:
            saxparser.parse(StringIO(input))
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

class SCons_XML(object):
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
        gen, mod = files.split(',')
        g.write_gen(gen)
        g.write_mod(mod)
    def write_gen(self, filename):
        if not filename:
            return
        f = self.fopen(filename)
        for v in self.values:
            f.write('\n<varlistentry id="%s%s">\n' %
                        (v.prefix, v.idfunc()))
            f.write('%s\n' % v.xml_term())
            f.write('<listitem>\n')
            for chunk in v.summary.body:
                f.write(str(chunk))
            if v.sets:
                s = ['&cv-link-%s;' % x for x in v.sets]
                f.write('<para>\n')
                f.write('Sets:  ' + ', '.join(s) + '.\n')
                f.write('</para>\n')
            if v.uses:
                u = ['&cv-link-%s;' % x for x in v.uses]
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
        if self.env_signatures:
            f.write('\n')
            for v in self.values:
                f.write('<!ENTITY %senv-%s "<%s>env.%s</%s>">\n' %
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
        if self.env_signatures:
            f.write('\n')
            for v in self.values:
                f.write('<!ENTITY %slink-env-%s \'<link linkend="%s%s"><%s>env.%s</%s></link>\'>\n' %
                            (v.prefix, v.idfunc(),
                             v.prefix, v.idfunc(),
                             v.tag, v.entityfunc(), v.tag))
        f.write('\n')
        f.write(Warning)

class SCons_XML_to_man(SCons_XML):
    def write(self, filename):
        """
        Converts the contents of the specified filename from DocBook XML
        to man page macros.

        This does not do an intelligent job.  In particular, it doesn't
        actually use the structured nature of XML to handle arbitrary
        input.  Instead, we're using text replacement and regular
        expression substitutions to convert observed patterns into the
        macros we want.  To the extent that we're relatively consistent
        with our input .xml, this works, but could easily break if handed
        input that doesn't match these specific expectations.
        """
        if not filename:
            return
        f = self.fopen(filename)
        chunks = []
        for v in self.values:
            chunks.extend(v.man_separator())
            chunks.extend(v.initial_man_chunks())
            chunks.extend(list(map(str, v.summary.body)))

        body = ''.join(chunks)

        # Simple transformation of examples into our defined macros for those.
        body = body.replace('<programlisting>', '.ES')
        body = body.replace('</programlisting>', '.EE')

        # Replace groupings of <para> tags and surrounding newlines
        # with single blank lines.
        body = body.replace('\n</para>\n<para>\n', '\n\n')
        body = body.replace('<para>\n', '')
        body = body.replace('<para>', '\n')
        body = body.replace('</para>\n', '')

        # Convert <variablelist> and its child tags.
        body = body.replace('<variablelist>\n', '.RS 10\n')
        # Handling <varlistentry> needs to be rationalized and made
        # consistent.  Right now, the <term> values map to arbitrary,
        # ad-hoc idioms in the current man page.
        body = re.compile(r'<varlistentry>\n<term><literal>([^<]*)</literal></term>\n<listitem>\n').sub(r'.TP 6\n.B \1\n', body)
        body = re.compile(r'<varlistentry>\n<term><parameter>([^<]*)</parameter></term>\n<listitem>\n').sub(r'.IP \1\n', body)
        body = re.compile(r'<varlistentry>\n<term>([^<]*)</term>\n<listitem>\n').sub(r'.HP 6\n.B \1\n', body)
        body = body.replace('</listitem>\n', '')
        body = body.replace('</varlistentry>\n', '')
        body = body.replace('</variablelist>\n', '.RE\n')

        # Get rid of unnecessary .IP macros, and unnecessary blank lines
        # in front of .IP macros.
        body = re.sub(r'\.EE\n\n+(?!\.IP)', '.EE\n.IP\n', body)
        body = body.replace('\n.EE\n.IP\n.ES\n', '\n.EE\n\n.ES\n')
        body = body.replace('\n.IP\n\'\\"', '\n\n\'\\"')

        # Convert various named entities and tagged names to nroff
        # in-line font conversions (\fB, \fI, \fP).
        body = re.sub('&(scons|SConstruct|SConscript|Dir|jar|Make|lambda);',
                      r'\\fB\1\\fP', body)
        body = re.sub('&(TARGET|TARGETS|SOURCE|SOURCES);', r'\\fB$\1\\fP', body)
        body = re.sub('&(target|source);', r'\\fI\1\\fP', body)
        body = re.sub('&b(-link)?-([^;]*);', r'\\fB\2\\fP()', body)
        body = re.sub('&cv(-link)?-([^;]*);', r'\\fB$\2\\fP', body)
        body = re.sub('&f(-link)?-env-([^;]*);', r'\\fBenv.\2\\fP()', body)
        body = re.sub('&f(-link)?-([^;]*);', r'\\fB\2\\fP()', body)
        body = re.sub(r'<(application|command|envar|filename|function|literal|option)>([^<]*)</\1>',
                      r'\\fB\2\\fP', body)
        body = re.sub(r'<(classname|emphasis|varname)>([^<]*)</\1>',
                      r'\\fI\2\\fP', body)

        # Convert groupings of font conversions (\fB, \fI, \fP) to
        # man page .B, .BR, .I, .IR, .R, .RB and .RI macros.
        body = re.compile(r'^\\f([BI])([^\\]* [^\\]*)\\fP\s*$', re.M).sub(r'.\1 "\2"', body)
        body = re.compile(r'^\\f([BI])(.*)\\fP\s*$', re.M).sub(r'.\1 \2', body)
        body = re.compile(r'^\\f([BI])(.*)\\fP(\S+)$', re.M).sub(r'.\1R \2 \3', body)
        body = re.compile(r'^(\.B)( .*)\\fP(.*)\\fB(.*)$', re.M).sub(r'\1R\2 \3 \4', body)
        body = re.compile(r'^(\.B)R?( .*)\\fP(.*)\\fI(.*)$', re.M).sub(r'\1I\2\3 \4', body)
        body = re.compile(r'^(\.I)( .*)\\fP\\fB(.*)\\fP\\fI(.*)$', re.M).sub(r'\1R\2 \3 \4', body)
        body = re.compile(r'^(\S+)\\f([BI])(.*)\\fP$', re.M).sub(r'.R\2 \1 \3', body)
        body = re.compile(r'^(\S+)\\f([BI])(.*)\\fP([^\s\\]+)$', re.M).sub(r'.R\2 \1 \3 \4', body)
        body = re.compile(r'^(\.R[BI].*[\S])\s+$;', re.M).sub(r'\1', body)

        # Convert &lt; and &gt; entities to literal < and > characters.
        body = body.replace('&lt;', '<')
        body = body.replace('&gt;', '>')

        # Backslashes.  Oh joy.
        body = re.sub(r'\\(?=[^f])', r'\\\\', body)
        body = re.compile("^'\\\\\\\\", re.M).sub("'\\\\", body)
        body = re.compile(r'^\.([BI]R?) ([^"]\S*\\\\\S+[^"])$', re.M).sub(r'.\1 "\2"', body)

        # Put backslashes in front of various hyphens that need
        # to be long em-dashes.
        body = re.compile(r'^\.([BI]R?) --', re.M).sub(r'.\1 \-\-', body)
        body = re.compile(r'^\.([BI]R?) -', re.M).sub(r'.\1 \-', body)
        body = re.compile(r'\\f([BI])-', re.M).sub(r'\\f\1\-', body)

        f.write(body)

class Proxy(object):
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

class SConsThing(Proxy):
    def idfunc(self):
        return self.name
    def xml_term(self):
        return '<term>%s</term>' % self.name

class Builder(SConsThing):
    description = 'builder'
    prefix = 'b-'
    tag = 'function'
    def xml_term(self):
        return ('<term><%s>%s()</%s></term>\n<term><%s>env.%s()</%s></term>' %
                (self.tag, self.name, self.tag, self.tag, self.name, self.tag))
    def entityfunc(self):
        return self.name
    def man_separator(self):
        return ['\n', "'\\" + '"'*69 + '\n']
    def initial_man_chunks(self):
        return [ '.IP %s()\n.IP env.%s()\n' % (self.name, self.name) ]

class Function(SConsThing):
    description = 'function'
    prefix = 'f-'
    tag = 'function'
    def args_to_xml(self, arg):
        s = ''.join(arg.body).strip()
        result = []
        for m in re.findall('([a-zA-Z/_]+=?|[^a-zA-Z/_]+)', s):
            if m[0] in string.letters:
                if m[-1] == '=':
                    result.append('<literal>%s</literal>=' % m[:-1])
                else:
                    result.append('<varname>%s</varname>' % m)
            else:
                result.append(m)
        return ''.join(result)
    def xml_term(self):
        try:
            arguments = self.arguments
        except AttributeError:
            arguments = ['()']
        result = []
        for arg in arguments:
            try:
                signature = arg.signature
            except AttributeError:
                signature = "both"
            s = self.args_to_xml(arg)
            if signature in ('both', 'global'):
                result.append('<term>%s%s</term>\n' % (self.name, s)) #<br>
            if signature in ('both', 'env'):
                result.append('<term><varname>env</varname>.%s%s</term>\n' % (self.name, s))
        return ''.join(result)
    def entityfunc(self):
        return self.name
    def man_separator(self):
        return ['\n', "'\\" + '"'*69 + '\n']
    def args_to_man(self, arg):
        """Converts the contents of an <arguments> tag, which
        specifies a function's calling signature, into a series
        of tokens that alternate between literal tokens
        (to be displayed in roman or bold face) and variable
        names (to be displayed in italics).

        This is complicated by the presence of Python "keyword=var"
        arguments, where "keyword=" should be displayed literally,
        and "var" should be displayed in italics.  We do this by
        detecting the keyword= var portion and appending it to the
        previous string, if any.
        """
        s = ''.join(arg.body).strip()
        result = []
        for m in re.findall('([a-zA-Z/_]+=?|[^a-zA-Z/_]+)', s):
            if m[-1] == '=' and result:
                if result[-1][-1] == '"':
                    result[-1] = result[-1][:-1] + m + '"'
                else:
                    result[-1] += m
            else:
                if ' ' in m:
                    m = '"%s"' % m
                result.append(m)
        return ' '.join(result)
    def initial_man_chunks(self):
        try:
            arguments = self.arguments
        except AttributeError:
            arguments = ['()']
        result = []
        for arg in arguments:
            try:
                signature = arg.signature
            except AttributeError:
                signature = "both"
            s = self.args_to_man(arg)
            if signature in ('both', 'global'):
                result.append('.TP\n.RI %s%s\n' % (self.name, s))
            if signature in ('both', 'env'):
                result.append('.TP\n.IR env .%s%s\n' % (self.name, s))
        return result

class Tool(SConsThing):
    description = 'tool'
    prefix = 't-'
    tag = 'literal'
    def idfunc(self):
        return self.name.replace('+', 'X')
    def entityfunc(self):
        return self.name
    def man_separator(self):
        return ['\n']
    def initial_man_chunks(self):
        return ['.IP %s\n' % self.name]

class Variable(SConsThing):
    description = 'construction variable'
    prefix = 'cv-'
    tag = 'envar'
    def entityfunc(self):
        return '$' + self.name
    def man_separator(self):
        return ['\n']
    def initial_man_chunks(self):
        return ['.IP %s\n' % self.name]

if output_type == '--man':
    processor_class = SCons_XML_to_man
elif output_type == '--xml':
    processor_class = SCons_XML_to_XML
else:
    sys.stderr.write("Unknown output type '%s'\n" % output_type)
    sys.exit(1)

if buildersfiles:
    g = processor_class([ Builder(b) for b in sorted(h.builders.values()) ],
                        env_signatures=True)
    g.write(buildersfiles)

if functionsfiles:
    g = processor_class([ Function(b) for b in sorted(h.functions.values()) ],
                        env_signatures=True)
    g.write(functionsfiles)

if toolsfiles:
    g = processor_class([ Tool(t) for t in sorted(h.tools.values()) ],
                        env_signatures=False)
    g.write(toolsfiles)

if variablesfiles:
    g = processor_class([ Variable(v) for v in sorted(h.cvars.values()) ],
                        env_signatures=False)
    g.write(variablesfiles)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
