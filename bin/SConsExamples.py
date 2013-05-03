#!/usr/bin/env python
#
# Module for handling SCons examples processing.
#

__doc__ = """
"""

import os
import re
import SConsDoc
from SConsDoc import tf as stf

#
# The available types for ExampleFile entries
#
FT_FILE = 0     # a physical file (=<file>)
FT_FILEREF = 1  # a reference     (=<scons_example_file>)

class ExampleFile:
    def __init__(self, type_=FT_FILE):
        self.type = type_
        self.name = ''
        self.content = ''
        self.chmod = ''
        
    def isFileRef(self):
        return self.type == FT_FILEREF

class ExampleFolder:
    def __init__(self):
        self.name = ''
        self.chmod = ''

class ExampleCommand:
    def __init__(self):
        self.edit = ''
        self.environment = ''
        self.output = ''
        self.cmd = ''
        self.suffix = ''

class ExampleOutput:
    def __init__(self):
        self.name = ''
        self.tools = ''
        self.os = ''
        self.commands = []
        
class ExampleInfo:
    def __init__(self):
        self.name = ''
        self.files = []
        self.folders = []
        self.outputs = []
        
    def getFileContents(self, fname):
        for f in self.files:
            if fname == f.name and not f.isFileRef():
                return f.content
            
        return ''

def readExampleInfos(fpath, examples):
    """ Add the example infos for the file fpath to the
        global dictionary examples.
    """

    # Create doctree    
    t = SConsDoc.SConsDocTree()
    t.parseXmlFile(fpath)
    
    # Parse scons_examples
    for e in stf.findAll(t.root, "scons_example", SConsDoc.dbxid, 
                         t.xpath_context, t.nsmap):
        n = ''
        if stf.hasAttribute(e, 'name'):
            n = stf.getAttribute(e, 'name')
        if n and n not in examples:
            i = ExampleInfo()
            i.name = n
            examples[n] = i
            
        # Parse file and directory entries
        for f in stf.findAll(e, "file", SConsDoc.dbxid, 
                             t.xpath_context, t.nsmap):
            fi = ExampleFile()
            if stf.hasAttribute(f, 'name'):
                fi.name = stf.getAttribute(f, 'name')
            if stf.hasAttribute(f, 'chmod'):
                fi.chmod = stf.getAttribute(f, 'chmod')
            fi.content = stf.getText(f)
            examples[n].files.append(fi)
        for d in stf.findAll(e, "directory", SConsDoc.dbxid, 
                             t.xpath_context, t.nsmap):
            di = ExampleFolder()
            if stf.hasAttribute(d, 'name'):
                di.name = stf.getAttribute(d, 'name')
            if stf.hasAttribute(d, 'chmod'):
                di.chmod = stf.getAttribute(d, 'chmod')
            examples[n].folders.append(di)


    # Parse scons_example_files
    for f in stf.findAll(t.root, "scons_example_file", SConsDoc.dbxid, 
                         t.xpath_context, t.nsmap):
        if stf.hasAttribute(f, 'example'):
            e = stf.getAttribute(f, 'example')
        else:
            continue
        fi = ExampleFile(FT_FILEREF)
        if stf.hasAttribute(f, 'name'):
            fi.name = stf.getAttribute(f, 'name')
        if stf.hasAttribute(f, 'chmod'):
            fi.chmod = stf.getAttribute(f, 'chmod')
        fi.content = stf.getText(f)
        examples[e].files.append(fi)
        
    
    # Parse scons_output
    for o in stf.findAll(t.root, "scons_output", SConsDoc.dbxid, 
                         t.xpath_context, t.nsmap):
        if stf.hasAttribute(o, 'example'):
            n = stf.getAttribute(o, 'example')
        else:
            continue

        eout = ExampleOutput()
        if stf.hasAttribute(o, 'name'):
            eout.name = stf.getAttribute(o, 'name')
        if stf.hasAttribute(o, 'tools'):
            eout.tools = stf.getAttribute(o, 'tools')
        if stf.hasAttribute(o, 'os'):
            eout.os = stf.getAttribute(o, 'os')

        for c in stf.findAll(o, "scons_output_command", SConsDoc.dbxid, 
                         t.xpath_context, t.nsmap):
            if stf.hasAttribute(c, 'suffix'):
                s = stf.getAttribute(c, 'suffix')
            else:
                continue

            oc = ExampleCommand()
            oc.suffix = s
            if stf.hasAttribute(c, 'edit'):
                oc.edit = stf.getAttribute(c, 'edit')
            if stf.hasAttribute(c, 'environment'):
                oc.environment = stf.getAttribute(c, 'environment')
            if stf.hasAttribute(c, 'output'):
                oc.output = stf.getAttribute(c, 'output')
            if stf.hasAttribute(c, 'cmd'):
                oc.cmd = stf.getAttribute(c, 'cmd')

            eout.commands.append(oc)

        examples[n].outputs.append(eout)

def readAllExampleInfos(dpath):
    """ Scan for XML files in the given directory and 
        collect together all relevant infos (files/folders,
        output commands) in a map, which gets returned.
    """
    examples = {}
    for path, dirs, files in os.walk(dpath):
        for f in files:
            if f.endswith('.xml'):
                fpath = os.path.join(path, f)
                if SConsDoc.isSConsXml(fpath):
                    readExampleInfos(fpath, examples)
                   
    return examples

generated_examples = os.path.join('doc','generated','examples')

def ensureExampleOutputsExist(dpath):
    """ Scan for XML files in the given directory and 
        ensure that for every example output we have a
        corresponding output file in the 'generated/examples'
        folder.
    """
    # Ensure that the output folder exists
    if not os.path.isdir(generated_examples):
        os.mkdir(generated_examples)
        
    examples = readAllExampleInfos(dpath)
    for key, value in examples.iteritems():
        # Process all scons_output tags
        for o in value.outputs:
            for c in o.commands:
                cpath = os.path.join(generated_examples, 
                                     key+'_'+c.suffix+'.out')
                if not os.path.isfile(cpath):
                    content = c.output
                    if not content:
                        content = "NO OUTPUT YET! Run the script to generate/update all examples."

                    f = open(cpath, 'w')
                    f.write("%s\n" % content)
                    f.close()
        # Process all scons_example_file tags
        for r in value.files:
            if r.isFileRef():
                # Get file's content
                content = value.getFileContents(r.name)
                fpath = os.path.join(generated_examples, 
                                     key+'_'+r.name.replace("/","_"))
                # Write file
                f = open(fpath, 'w')
                f.write("%s\n" % content)
                f.close()

def collectSConsExampleNames(fpath):
    """ Return a set() of example names, used in the given file fpath.
    """
    names = set()
    suffixes = {}
    failed_suffixes = False

    # Create doctree    
    t = SConsDoc.SConsDocTree()
    t.parseXmlFile(fpath)
    
    # Parse it
    for e in stf.findAll(t.root, "scons_example", SConsDoc.dbxid, 
                         t.xpath_context, t.nsmap):
        n = ''
        if stf.hasAttribute(e, 'name'):
            n = stf.getAttribute(e, 'name')
        if n:
            names.add(n)
            if n not in suffixes:
                suffixes[n] = []
        else:
            print "Error: Example in file '%s' is missing a name!" % fpath
            failed_suffixes = True
    
    for o in stf.findAll(t.root, "scons_output", SConsDoc.dbxid, 
                         t.xpath_context, t.nsmap):
        n = ''
        if stf.hasAttribute(o, 'example'):
            n = stf.getAttribute(o, 'example')
        else:
            print "Error: scons_output in file '%s' is missing an example name!" % fpath
            failed_suffixes = True
            
        if n not in suffixes:
            print "Error: scons_output in file '%s' is referencing non-existent example '%s'!" % (fpath, n)
            failed_suffixes = True
            continue
            
        for c in stf.findAll(o, "scons_output_command", SConsDoc.dbxid, 
                         t.xpath_context, t.nsmap):
            s = ''
            if stf.hasAttribute(c, 'suffix'):
                s = stf.getAttribute(c, 'suffix')
            else:
                print "Error: scons_output_command in file '%s' (example '%s') is missing a suffix!" % (fpath, n)
                failed_suffixes = True
            
            if s not in suffixes[n]:
                suffixes[n].append(s)
            else:
                print "Error: scons_output_command in file '%s' (example '%s') is using a duplicate suffix '%s'!" % (fpath, n, s)
                failed_suffixes = True
    
    return names, failed_suffixes

def exampleNamesAreUnique(dpath):
    """ Scan for XML files in the given directory and 
        check whether the scons_example names are unique.
    """
    unique = True
    allnames = set()
    for path, dirs, files in os.walk(dpath):
        for f in files:
            if f.endswith('.xml'):
                fpath = os.path.join(path, f)
                if SConsDoc.isSConsXml(fpath):
                    names, failed_suffixes = collectSConsExampleNames(fpath)
                    if failed_suffixes:
                        unique = False
                    i = allnames.intersection(names)
                    if i:
                        print "Not unique in %s are: %s" % (fpath, ', '.join(i))
                        unique = False
                    
                    allnames |= names
                   
    return unique

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
