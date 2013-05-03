#!/usr/bin/env python
#
# Process a list of Python and/or XML files containing SCons documentation.
#
# This script creates formatted lists of the Builders, functions, Tools
# or construction variables documented in the specified XML files.
#
# Depending on the options, the lists are output in either
# DocBook-formatted generated XML files containing the summary text
# and/or .mod files containing the ENTITY definitions for each item.
#
import getopt
import os
import re
import string
import sys
try:
    from io import StringIO     # usable as of 2.6; takes unicode only
except ImportError:
    # No 'io' module or no StringIO in io
    exec('from cStringIO import StringIO')

import SConsDoc

base_sys_path = [os.getcwd() + '/build/test-tar-gz/lib/scons'] + sys.path

helpstr = """\
Usage: scons-proc.py [-b file(s)] [-f file(s)] [-t file(s)] [-v file(s)]
                     [infile ...]
Options:
  -b file(s)        dump builder information to the specified file(s)
  -f file(s)        dump function information to the specified file(s)
  -t file(s)        dump tool information to the specified file(s)
  -v file(s)        dump variable information to the specified file(s)
  
  Regard that each -[btv] argument is a pair of
  comma-separated .gen,.mod file names.
  
"""

opts, args = getopt.getopt(sys.argv[1:],
                           "b:f:ht:v:",
                           ['builders=', 'help',
                            'tools=', 'variables='])

buildersfiles = None
functionsfiles = None
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
    elif o in ['-t', '--tools']:
        toolsfiles = a
    elif o in ['-v', '--variables']:
        variablesfiles = a

def parse_docs(args, include_entities=True):
    h = SConsDoc.SConsDocHandler()
    for f in args:
        if include_entities:
            try:
                h.parseXmlFile(f)
            except:
                sys.stderr.write("error in %s\n" % f)
                raise
        else:
            content = open(f).read()
            if content:
                try:
                    h.parseContent(content, include_entities)
                except:
                    sys.stderr.write("error in %s\n" % f)
                    raise
    return h

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
    
    def write(self, files):
        gen, mod = files.split(',')
        self.write_gen(gen)
        self.write_mod(mod)
        
    def write_gen(self, filename):
        if not filename:
            return
        # Try to split off .gen filename
        if filename.count(','):
            fl = filename.split(',')
            filename = fl[0]
        f = self.fopen(filename)
        
        # Write XML header
        f.write("""<?xml version='1.0'?>
<variablelist xmlns="%s"
              xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xsi:schemaLocation="%s scons.xsd">

""" % (SConsDoc.dbxsd, SConsDoc.dbxsd))
        f.write(Warning)
        
        for v in self.values:
            f.write('\n<varlistentry id="%s%s">\n' %
                        (v.prefix, v.idfunc()))
            f.write('%s\n' % v.xml_term())
            f.write('<listitem>\n')
            # TODO: write summary
            f.write('<para>\n')
            if v.summary:
                pass
            f.write('</para>\n')
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
            
        # Write end tag
        f.write('\n</variablelist>\n')
            
    def write_mod(self, filename):
        try:
            description = self.values[0].description
        except:
            description = ""
        if not filename:
            return
        # Try to split off .mod filename
        if filename.count(','):
            fl = filename.split(',')
            filename = fl[1]
        f = self.fopen(filename)
        f.write(Warning)
        f.write('\n')
        f.write(Regular_Entities_Header % description)
        f.write('\n')
        for v in self.values:
            f.write('<!ENTITY %s%s "<%s xmlns=\'%s\'>%s</%s>">\n' %
                        (v.prefix, v.idfunc(),
                         v.tag, SConsDoc.dbxsd, v.entityfunc(), v.tag))
        if self.env_signatures:
            f.write('\n')
            for v in self.values:
                f.write('<!ENTITY %senv-%s "<%s xmlns=\'%s\'>env.%s</%s>">\n' %
                            (v.prefix, v.idfunc(),
                             v.tag, SConsDoc.dbxsd, v.entityfunc(), v.tag))
        f.write('\n')
        f.write(Warning)
        f.write('\n')
        f.write(Link_Entities_Header % description)
        f.write('\n')
        for v in self.values:
            f.write('<!ENTITY %slink-%s "<link linkend=\'%s%s\' xmlns=\'%s\'><%s>%s</%s></link>">\n' %
                        (v.prefix, v.idfunc(),
                         v.prefix, v.idfunc(), SConsDoc.dbxsd,
                         v.tag, v.entityfunc(), v.tag))
        if self.env_signatures:
            f.write('\n')
            for v in self.values:
                f.write('<!ENTITY %slink-env-%s "<link linkend=\'%s%s\' xmlns=\'%s\'><%s>env.%s</%s></link>">\n' %
                            (v.prefix, v.idfunc(),
                             v.prefix, v.idfunc(), SConsDoc.dbxsd,
                             v.tag, v.entityfunc(), v.tag))
        f.write('\n')
        f.write(Warning)

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
        return ('<term><synopsis><%s>%s()</%s></synopsis>\n<synopsis><%s>env.%s()</%s></synopsis></term>' %
                (self.tag, self.name, self.tag, self.tag, self.name, self.tag))
        
    def entityfunc(self):
        return self.name

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
        result = ['<term>']
        for arg in arguments:
            try:
                signature = arg.signature
            except AttributeError:
                signature = "both"
            s = arg # TODO: self.args_to_xml(arg)
            if signature in ('both', 'global'):
                result.append('<synopsis>%s%s</synopsis>\n' % (self.name, s)) #<br>
            if signature in ('both', 'env'):
                result.append('<synopsis><varname>env</varname>.%s%s</synopsis>' % (self.name, s))
        result.append('</term>')
        return ''.join(result)
    
    def entityfunc(self):
        return self.name

class Tool(SConsThing):
    description = 'tool'
    prefix = 't-'
    tag = 'literal'
    
    def idfunc(self):
        return self.name.replace('+', 'X')
    
    def entityfunc(self):
        return self.name

class Variable(SConsThing):
    description = 'construction variable'
    prefix = 'cv-'
    tag = 'envar'
    
    def entityfunc(self):
        return '$' + self.name

def write_output_files(h, buildersfiles, functionsfiles,
                         toolsfiles, variablesfiles, write_func):
    if buildersfiles:
        g = processor_class([ Builder(b) for b in sorted(h.builders.values()) ],
                            env_signatures=True)
        write_func(g, buildersfiles)
    
    if functionsfiles:
        g = processor_class([ Function(b) for b in sorted(h.functions.values()) ],
                            env_signatures=True)
        write_func(g, functionsfiles)
    
    if toolsfiles:
        g = processor_class([ Tool(t) for t in sorted(h.tools.values()) ],
                            env_signatures=False)
        write_func(g, toolsfiles)
    
    if variablesfiles:
        g = processor_class([ Variable(v) for v in sorted(h.cvars.values()) ],
                            env_signatures=False)
        write_func(g, variablesfiles)

processor_class = SCons_XML

# Step 1: Creating entity files for builders, functions,...
h = parse_docs(args, False)
write_output_files(h, buildersfiles, functionsfiles, toolsfiles,
                   variablesfiles, SCons_XML.write_mod)

# Step 2: Patching the include paths for entity definitions in XML files
os.system('python bin/docs-correct-mod-paths.py')

# Step 3: Validating all input files
print "Validating files against SCons XSD..."
if SConsDoc.validate_all_xml():
    print "OK"
else:
    print "Validation failed! Please correct the errors above and try again."

# Step 4: Creating actual documentation snippets, using the
#         fully resolved and updated entities from the *.mod files.
h = parse_docs(args, True)
write_output_files(h, buildersfiles, functionsfiles, toolsfiles,
                   variablesfiles, SCons_XML.write)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
