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
import sys

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
  
  The "files" argument following a -[bftv] argument is expected to
  be a comma-separated pair of names like: foo.gen,foo.mod
  
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
            except Exception as e:
                print("error parsing %s\n" % f, file=sys.stderr)
                print(str(e), file=sys.stderr)
                sys.exit(1)
        else:
            # mode we read (text/bytes) has to match handling in SConsDoc
            with open(f, 'r') as fp:
                content = fp.read()
            if content:
                try:
                    h.parseContent(content, include_entities)
                except Exception as e:
                    print("error parsing %s\n" % f, file=sys.stderr)
                    print(str(e), file=sys.stderr)
                    sys.exit(1)
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

  Entities that are links to the %s entries

-->
"""

class SCons_XML:
    def __init__(self, entries, **kw):
        self.values = entries
        for k, v in kw.items():
            setattr(self, k, v)
            
    def fopen(self, name, mode='w'):
        if name == '-':
            return sys.stdout
        return open(name, mode)
    
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
            
            if v.sets:
                added = True
                vp = stf.newNode("para")
                stf.setText(vp, 'Sets: ')
                for x in v.sets[:-1]:
                    stf.appendCvLink(vp, x, ', ')
                stf.appendCvLink(vp, v.sets[-1], '.')
                stf.appendNode(vl, vp)

            if v.uses:
                added = True
                vp = stf.newNode("para")
                stf.setText(vp, 'Uses: ')
                for x in v.uses[:-1]:
                    stf.appendCvLink(vp, x, ', ')
                stf.appendCvLink(vp, v.uses[-1], '.')
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
        f.close()
            
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
        f.close()

class Proxy:
    def __init__(self, subject):
        """Wrap an object as a Proxy object"""
        self.__subject = subject

    def __getattr__(self, name):
        """Retrieve an attribute from the wrapped object.

        If the named attribute doesn't exist, AttributeError is raised
        """
        return getattr(self.__subject, name)

    def get(self):
        """Retrieve the entire wrapped object"""
        return self.__subject

    def __eq__(self, other):
        if issubclass(other.__class__, self.__subject.__class__):
            return self.__subject == other
        return self.__dict__ == other.__dict__

    ## def __lt__(self, other):
    ##     if issubclass(other.__class__, self.__subject.__class__):
    ##         return self.__subject < other
    ##     return self.__dict__ < other.__dict__

class SConsThing(Proxy):
    """Base class for the SConsDoc special elements"""
    def idfunc(self):
        return self.name
    
    def xml_terms(self):
        e = stf.newNode("term")
        stf.setText(e, self.name)
        return [e]

class Builder(SConsThing):
    """Generate the descriptions and entities for <builder> elements"""
    description = 'builder'
    prefix = 'b-'
    tag = 'function'
    
    def xml_terms(self):
        """emit xml for an scons builder

        builders don't show a full signature, just func()
        """
        # build term for global function
        gterm = stf.newNode("term")
        func = stf.newSubNode(gterm, Builder.tag)
        stf.setText(func, self.name)
        stf.setTail(func, '()')

        # build term for env. method
        mterm = stf.newNode("term")
        inst = stf.newSubNode(mterm, "replaceable")
        stf.setText(inst, "env")
        stf.setTail(inst, ".")
        # we could use <function> here, but it's a "method"
        meth = stf.newSubNode(mterm, "methodname")
        stf.setText(meth, self.name)
        stf.setTail(meth, '()')

        return [gterm, mterm]
            
    def entityfunc(self):
        return self.name

class Function(SConsThing):
    """Generate the descriptions and entities for <scons_function> elements"""
    description = 'function'
    prefix = 'f-'
    tag = 'function'
    
    def xml_terms(self):
        """emit xml for an scons function

        The signature attribute controls whether to emit the
        global function, the environment method, or both.
        """
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
            sig = stf.getText(arg).strip()[1:-1]  # strip (), temporarily
            if signature in ('both', 'global'):
                # build term for global function
                gterm = stf.newNode("term")
                func = stf.newSubNode(gterm, Function.tag)
                stf.setText(func, self.name)
                if sig:
                    # if there are parameters, use that entity
                    stf.setTail(func, "(")
                    s = stf.newSubNode(gterm, "parameter")
                    stf.setText(s, sig)
                    stf.setTail(s, ")")
                else:
                    stf.setTail(func, "()")
                tlist.append(gterm)
            if signature in ('both', 'env'):
                # build term for env. method
                mterm = stf.newNode("term")
                inst = stf.newSubNode(mterm, "replaceable")
                stf.setText(inst, "env")
                stf.setTail(inst, ".")
                # we could use <function> here, but it's a "method"
                meth = stf.newSubNode(mterm, "methodname")
                stf.setText(meth, self.name)
                if sig:
                    # if there are parameters, use that entity
                    stf.setTail(meth, "(")
                    s = stf.newSubNode(mterm, "parameter")
                    stf.setText(s, sig)
                    stf.setTail(s, ")")
                else:
                    stf.setTail(meth, "()")
                tlist.append(mterm)

        if not tlist:
            tlist.append(stf.newNode("term"))
        return tlist
    
    def entityfunc(self):
        return self.name

class Tool(SConsThing):
    """Generate the descriptions and entities for <tool> elements"""
    description = 'tool'
    prefix = 't-'
    tag = 'literal'
    
    def idfunc(self):
        return self.name.replace('+', 'X')
    
    def entityfunc(self):
        return self.name

class Variable(SConsThing):
    """Generate the descriptions and entities for <cvar> elements"""
    description = 'construction variable'
    prefix = 'cv-'
    tag = 'envar'

    def xml_terms(self):
        term = stf.newNode("term")
        var = stf.newSubNode(term, Variable.tag)
        stf.setText(var, self.name)
        return [term]
    
    def entityfunc(self):
        return '$' + self.name

def write_output_files(h, buildersfiles, functionsfiles,
                       toolsfiles, variablesfiles, write_func):
    if buildersfiles:
        g = processor_class([Builder(b) for b in sorted(h.builders.values())],
                            env_signatures=True)
        write_func(g, buildersfiles)
    
    if functionsfiles:
        g = processor_class([Function(b) for b in sorted(h.functions.values())],
                            env_signatures=True)
        write_func(g, functionsfiles)
    
    if toolsfiles:
        g = processor_class([Tool(t) for t in sorted(h.tools.values())],
                            env_signatures=False)
        write_func(g, toolsfiles)
    
    if variablesfiles:
        g = processor_class([Variable(v) for v in sorted(h.cvars.values())],
                            env_signatures=False)
        write_func(g, variablesfiles)

processor_class = SCons_XML

# Step 1: Creating entity files for builders, functions,...
print("Generating entity files...")
h = parse_docs(args, include_entities=False)
write_output_files(h, buildersfiles, functionsfiles, toolsfiles,
                   variablesfiles, SCons_XML.write_mod)

# Step 2: Validating all input files
print("Validating files against SCons XSD...")
if SConsDoc.validate_all_xml(['SCons']):
    print("OK")
else:
    print("Validation failed! Please correct the errors above and try again.")
    sys.exit(1)

# Step 3: Creating actual documentation snippets, using the
#         fully resolved and updated entities from the *.mod files.
print("Updating documentation for builders, tools and functions...")
h = parse_docs(args, include_entities=True)
write_output_files(h, buildersfiles, functionsfiles, toolsfiles,
                   variablesfiles, SCons_XML.write)
print("Done")

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
