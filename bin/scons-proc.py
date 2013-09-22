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
from SConsDoc import tf as stf

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
        for k, v in list(kw.items()):
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
            
        # Start new XML file
        root = stf.newXmlTree("variablelist")
        
        for v in self.values:
            
            ve = stf.newNode("varlistentry")
            stf.setAttribute(ve, 'id', '%s%s' % (v.prefix, v.idfunc()))
            for t in v.xml_terms():
                stf.appendNode(ve, t)
            vl = stf.newNode("listitem")
            added = False
            if v.summary is not None:
                for s in v.summary:
                    added = True
                    stf.appendNode(vl, stf.copyNode(s))
            
            if len(v.sets):
                added = True
                vp = stf.newNode("para")
                s = ['&cv-link-%s;' % x for x in v.sets]
                stf.setText(vp, 'Sets:  ' + ', '.join(s) + '.')
                stf.appendNode(vl, vp)
            if len(v.uses):
                added = True
                vp = stf.newNode("para")
                u = ['&cv-link-%s;' % x for x in v.uses]
                stf.setText(vp, 'Uses:  ' + ', '.join(u) + '.')
                stf.appendNode(vl, vp)
                
            # Still nothing added to this list item?
            if not added:
                # Append an empty para
                vp = stf.newNode("para")
                stf.appendNode(vl, vp)
                
            stf.appendNode(ve, vl)
            stf.appendNode(root, ve)
            
        # Write file        
        f = self.fopen(filename)
        stf.writeGenTree(root, f)
            
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
    
    def xml_terms(self):
        e = stf.newNode("term")
        stf.setText(e, self.name)
        return [e]

class Builder(SConsThing):
    description = 'builder'
    prefix = 'b-'
    tag = 'function'
    
    def xml_terms(self):
        ta = stf.newNode("term")
        b = stf.newNode(self.tag)
        stf.setText(b, self.name+'()')
        stf.appendNode(ta, b)
        tb = stf.newNode("term")
        b = stf.newNode(self.tag)
        stf.setText(b, 'env.'+self.name+'()')
        stf.appendNode(tb, b)
        return [ta, tb]
            
    def entityfunc(self):
        return self.name

class Function(SConsThing):
    description = 'function'
    prefix = 'f-'
    tag = 'function'
    
    def xml_terms(self):
        if self.arguments is None:
            a = stf.newNode("arguments")
            stf.setText(a, '()')
            arguments = [a]
        else:
            arguments = self.arguments
        tlist = []
        for arg in arguments:
            signature = 'both'
            if stf.hasAttribute(arg, 'signature'):
                signature = stf.getAttribute(arg, 'signature')
            s = stf.getText(arg).strip()
            if signature in ('both', 'global'):
                t = stf.newNode("term")
                syn = stf.newNode("literal")
                stf.setText(syn, '%s%s' % (self.name, s))
                stf.appendNode(t, syn)
                tlist.append(t)
            if signature in ('both', 'env'):
                t = stf.newNode("term")
                syn = stf.newNode("literal")
                stf.setText(syn, 'env.%s%s' % (self.name, s))
                stf.appendNode(t, syn)
                tlist.append(t)

        if not tlist:
            tlist.append(stf.newNode("term"))
        return tlist
    
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
print("Generating entity files...")
h = parse_docs(args, False)
write_output_files(h, buildersfiles, functionsfiles, toolsfiles,
                   variablesfiles, SCons_XML.write_mod)

# Step 2: Validating all input files
print("Validating files against SCons XSD...")
if SConsDoc.validate_all_xml(['src']):
    print("OK")
else:
    print("Validation failed! Please correct the errors above and try again.")

# Step 3: Creating actual documentation snippets, using the
#         fully resolved and updated entities from the *.mod files.
print("Updating documentation for builders, tools and functions...")
h = parse_docs(args, True)
write_output_files(h, buildersfiles, functionsfiles, toolsfiles,
                   variablesfiles, SCons_XML.write)
print("Done")

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
