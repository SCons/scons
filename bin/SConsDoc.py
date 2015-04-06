#!/usr/bin/env python
#
# Copyright (c) 2010 The SCons Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#
# Module for handling SCons documentation processing.
#

__doc__ = """
This module parses home-brew XML files that document various things
in SCons.  Right now, it handles Builders, functions, construction
variables, and Tools, but we expect it to get extended in the future.

In general, you can use any DocBook tag in the input, and this module
just adds processing various home-brew tags to try to make life a
little easier.

Builder example:

    <builder name="BUILDER">
    <summary>
    <para>This is the summary description of an SCons Builder.
    It will get placed in the man page,
    and in the appropriate User's Guide appendix.
    The name of any builder may be interpolated
    anywhere in the document by specifying the
    &b-BUILDER; element.  It need not be on a line by itself.</para>

    Unlike normal XML, blank lines are significant in these
    descriptions and serve to separate paragraphs.
    They'll get replaced in DocBook output with appropriate tags
    to indicate a new paragraph.

    <example>
    print "this is example code, it will be offset and indented"
    </example>
    </summary>
    </builder>

Function example:

    <scons_function name="FUNCTION">
    <arguments>
    (arg1, arg2, key=value)
    </arguments>
    <summary>
    <para>This is the summary description of an SCons function.
    It will get placed in the man page,
    and in the appropriate User's Guide appendix.
    The name of any builder may be interpolated
    anywhere in the document by specifying the
    &f-FUNCTION; element.  It need not be on a line by itself.</para>

    <example>
    print "this is example code, it will be offset and indented"
    </example>
    </summary>
    </scons_function>

Construction variable example:

    <cvar name="VARIABLE">
    <summary>
    <para>This is the summary description of a construction variable.
    It will get placed in the man page,
    and in the appropriate User's Guide appendix.
    The name of any construction variable may be interpolated
    anywhere in the document by specifying the
    &t-VARIABLE; element.  It need not be on a line by itself.</para>

    <example>
    print "this is example code, it will be offset and indented"
    </example>
    </summary>
    </cvar>

Tool example:

    <tool name="TOOL">
    <summary>
    <para>This is the summary description of an SCons Tool.
    It will get placed in the man page,
    and in the appropriate User's Guide appendix.
    The name of any tool may be interpolated
    anywhere in the document by specifying the
    &t-TOOL; element. It need not be on a line by itself.</para>

    <example>
    print "this is example code, it will be offset and indented"
    </example>
    </summary>
    </tool>
"""

import imp
import os.path
import re
import sys
import copy

# Do we have libxml2/libxslt/lxml?
has_libxml2 = True
try:
    import libxml2
    import libxslt
except:
    has_libxml2 = False
    try:
        import lxml
    except:
        raise ImportError("Failed to import either libxml2/libxslt or lxml")

has_etree = False
if not has_libxml2:
    try:
        from lxml import etree
        has_etree = True
    except ImportError:
        pass
if not has_etree:
    try:
        # Python 2.5
        import xml.etree.cElementTree as etree
    except ImportError:
        try:
            # Python 2.5
            import xml.etree.ElementTree as etree
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree
                except ImportError:
                    raise ImportError("Failed to import ElementTree from any known place")

re_entity = re.compile("\&([^;]+);")
re_entity_header = re.compile("<!DOCTYPE\s+sconsdoc\s+[^\]]+\]>")

# Namespace for the SCons Docbook XSD
dbxsd="http://www.scons.org/dbxsd/v1.0"
# Namespace map identifier for the SCons Docbook XSD
dbxid="dbx"
# Namespace for schema instances
xsi = "http://www.w3.org/2001/XMLSchema-instance"

# Header comment with copyright
copyright_comment = """
__COPYRIGHT__

This file is processed by the bin/SConsDoc.py module.
See its __doc__ string for a discussion of the format.
"""

def isSConsXml(fpath):
    """ Check whether the given file is a SCons XML file, i.e. it
        contains the default target namespace definition.
    """
    try:
        f = open(fpath,'r')
        content = f.read()
        f.close()
        if content.find('xmlns="%s"' % dbxsd) >= 0:
            return True
    except:
        pass
    
    return False 

def remove_entities(content):
    # Cut out entity inclusions
    content = re_entity_header.sub("", content, re.M)
    # Cut out entities themselves
    content = re_entity.sub(lambda match: match.group(1), content)
    
    return content

default_xsd = os.path.join('doc','xsd','scons.xsd')

ARG = "dbscons"

class Libxml2ValidityHandler:
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def error(self, msg, data):
        if data != ARG:
            raise Exception, "Error handler did not receive correct argument"
        self.errors.append(msg)

    def warning(self, msg, data):
        if data != ARG:
            raise Exception, "Warning handler did not receive correct argument"
        self.warnings.append(msg)


class DoctypeEntity:
    def __init__(self, name_, uri_):
        self.name = name_
        self.uri = uri_
        
    def getEntityString(self):
        txt = """    <!ENTITY %(perc)s %(name)s SYSTEM "%(uri)s">
    %(perc)s%(name)s;
""" % {'perc' : perc, 'name' : self.name, 'uri' : self.uri}

        return txt
        
class DoctypeDeclaration:
    def __init__(self, name_=None):
        self.name = name_
        self.entries = []
        if self.name is None:
            # Add default entries
            self.name = "sconsdoc"
            self.addEntity("scons", "../scons.mod")
            self.addEntity("builders-mod", "builders.mod")
            self.addEntity("functions-mod", "functions.mod")
            self.addEntity("tools-mod", "tools.mod")
            self.addEntity("variables-mod", "variables.mod")
        
    def addEntity(self, name, uri):
        self.entries.append(DoctypeEntity(name, uri))
        
    def createDoctype(self):
        content = '<!DOCTYPE %s [\n' % self.name
        for e in self.entries:
            content += e.getEntityString()
        content += ']>\n'
        
        return content

if not has_libxml2:
    class TreeFactory:
        def __init__(self):
            pass
        
        def newNode(self, tag):
            return etree.Element(tag)

        def newEtreeNode(self, tag, init_ns=False):
            if init_ns:
                NSMAP = {None: dbxsd,
                         'xsi' : xsi}
                return etree.Element(tag, nsmap=NSMAP)

            return etree.Element(tag)
        
        def copyNode(self, node):
            return copy.deepcopy(node)
        
        def appendNode(self, parent, child):
            parent.append(child)

        def hasAttribute(self, node, att):
            return att in node.attrib
        
        def getAttribute(self, node, att):
            return node.attrib[att]
        
        def setAttribute(self, node, att, value):
            node.attrib[att] = value
            
        def getText(self, root):
            return root.text

        def setText(self, root, txt):
            root.text = txt

        def writeGenTree(self, root, fp):
            dt = DoctypeDeclaration()
            fp.write(etree.tostring(root, xml_declaration=True, 
                                    encoding="UTF-8", pretty_print=True, 
                                    doctype=dt.createDoctype()))

        def writeTree(self, root, fpath):
            fp = open(fpath, 'w')
            fp.write(etree.tostring(root, xml_declaration=True, 
                                    encoding="UTF-8", pretty_print=True))            
            fp.close()

        def prettyPrintFile(self, fpath):
            fin = open(fpath,'r')
            tree = etree.parse(fin)
            pretty_content = etree.tostring(tree, pretty_print=True)
            fin.close()
    
            fout = open(fpath,'w')
            fout.write(pretty_content)
            fout.close()

        def decorateWithHeader(self, root):
            root.attrib["{"+xsi+"}schemaLocation"] = "%s %s/scons.xsd" % (dbxsd, dbxsd)
            return root
            
        def newXmlTree(self, root):
            """ Return a XML file tree with the correct namespaces set,
                the element root as top entry and the given header comment.
            """
            NSMAP = {None: dbxsd,
                     'xsi' : xsi}
            t = etree.Element(root, nsmap=NSMAP)
            return self.decorateWithHeader(t)
        
        def validateXml(self, fpath, xmlschema_context):
            # Use lxml
            xmlschema = etree.XMLSchema(xmlschema_context)
            try:
                doc = etree.parse(fpath)
            except Exception, e:
                print "ERROR: %s fails to parse:"%fpath
                print e
                return False
            doc.xinclude()
            try:
                xmlschema.assertValid(doc)
            except Exception, e:
                print "ERROR: %s fails to validate:" % fpath
                print e
                return False
            return True

        def findAll(self, root, tag, ns=None, xp_ctxt=None, nsmap=None):
            expression = ".//{%s}%s" % (nsmap[ns], tag)
            if not ns or not nsmap:
                expression = ".//%s" % tag
            return root.findall(expression)

        def findAllChildrenOf(self, root, tag, ns=None, xp_ctxt=None, nsmap=None):
            expression = "./{%s}%s/*" % (nsmap[ns], tag)
            if not ns or not nsmap:
                expression = "./%s/*" % tag
            return root.findall(expression)

        def convertElementTree(self, root):
            """ Convert the given tree of etree.Element
                entries to a list of tree nodes for the
                current XML toolkit.
            """
            return [root]
        
else:        
    class TreeFactory:
        def __init__(self):
            pass
        
        def newNode(self, tag):
            return libxml2.newNode(tag)

        def newEtreeNode(self, tag, init_ns=False):
            return etree.Element(tag)
        
        def copyNode(self, node):
            return node.copyNode(1)
        
        def appendNode(self, parent, child):
            if hasattr(parent, 'addChild'):
                parent.addChild(child)
            else:
                parent.append(child)

        def hasAttribute(self, node, att):
            if hasattr(node, 'hasProp'):
                return node.hasProp(att)
            return att in node.attrib
        
        def getAttribute(self, node, att):
            if hasattr(node, 'prop'):
                return node.prop(att)
            return node.attrib[att]

        def setAttribute(self, node, att, value):
            if hasattr(node, 'setProp'):
                node.setProp(att, value)
            else:
                node.attrib[att] = value
                
        def getText(self, root):
            if hasattr(root, 'getContent'):
                return root.getContent()
            return root.text

        def setText(self, root, txt):
            if hasattr(root, 'setContent'):
                root.setContent(txt)
            else:
                root.text = txt

        def writeGenTree(self, root, fp):
            doc = libxml2.newDoc('1.0')
            dtd = doc.newDtd("sconsdoc", None, None)
            doc.addChild(dtd)
            doc.setRootElement(root)
            content = doc.serialize("UTF-8", 1)
            dt = DoctypeDeclaration()
            # This is clearly a hack, but unfortunately libxml2
            # doesn't support writing PERs (Parsed Entity References).
            # So, we simply replace the empty doctype with the
            # text we need...
            content = content.replace("<!DOCTYPE sconsdoc>", dt.createDoctype())
            fp.write(content)
            doc.freeDoc()

        def writeTree(self, root, fpath):
            fp = open(fpath, 'w')
            doc = libxml2.newDoc('1.0')
            doc.setRootElement(root)
            fp.write(doc.serialize("UTF-8", 1))
            doc.freeDoc()
            fp.close()

        def prettyPrintFile(self, fpath):
            # Read file and resolve entities
            doc = libxml2.readFile(fpath, None, libxml2d.XML_PARSE_NOENT)
            fp = open(fpath, 'w')
            # Prettyprint
            fp.write(doc.serialize("UTF-8", 1))
            fp.close()
            # Cleanup
            doc.freeDoc()

        def decorateWithHeader(self, root):
            # Register the namespaces
            ns = root.newNs(dbxsd, None)
            xi = root.newNs(xsi, 'xsi')
            root.setNs(ns)  #put this node in the target namespace
    
            root.setNsProp(xi, 'schemaLocation', "%s %s/scons.xsd" % (dbxsd, dbxsd))
        
            return root

        def newXmlTree(self, root):
            """ Return a XML file tree with the correct namespaces set,
                the element root as top entry and the given header comment.
            """
            t = libxml2.newNode(root)
            return self.decorateWithHeader(t)

        def validateXml(self, fpath, xmlschema_context):
            # Create validation context
            validation_context = xmlschema_context.schemaNewValidCtxt()
            # Set error/warning handlers
            eh = Libxml2ValidityHandler()
            validation_context.setValidityErrorHandler(eh.error, eh.warning, ARG)
            # Read file and resolve entities
            doc = libxml2.readFile(fpath, None, libxml2.XML_PARSE_NOENT)
            doc.xincludeProcessFlags(libxml2.XML_PARSE_NOENT)
            err = validation_context.schemaValidateDoc(doc)
            # Cleanup
            doc.freeDoc()
            del validation_context
        
            if err or eh.errors:
                for e in eh.errors:
                    print e.rstrip("\n")
                print "%s fails to validate" % fpath
                return False
                
            return True

        def findAll(self, root, tag, ns=None, xpath_context=None, nsmap=None):
            if hasattr(root, 'xpathEval') and xpath_context:
                # Use the xpath context
                xpath_context.setContextNode(root)
                expression = ".//%s" % tag
                if ns:
                    expression = ".//%s:%s" % (ns, tag)
                return xpath_context.xpathEval(expression)
            else:
                expression = ".//{%s}%s" % (nsmap[ns], tag)
                if not ns or not nsmap:
                    expression = ".//%s" % tag
                return root.findall(expression)

        def findAllChildrenOf(self, root, tag, ns=None, xpath_context=None, nsmap=None):
            if hasattr(root, 'xpathEval') and xpath_context:
                # Use the xpath context
                xpath_context.setContextNode(root)
                expression = "./%s/node()" % tag
                if ns:
                    expression = "./%s:%s/node()" % (ns, tag)
                
                return xpath_context.xpathEval(expression)
            else:
                expression = "./{%s}%s/node()" % (nsmap[ns], tag)
                if not ns or not nsmap:
                    expression = "./%s/node()" % tag
                return root.findall(expression)

        def expandChildElements(self, child):
            """ Helper function for convertElementTree,
                converts a single child recursively.
            """
            nchild = self.newNode(child.tag)
            # Copy attributes
            for key, val in child.attrib:
                self.setAttribute(nchild, key, val)
            elements = []
            # Add text
            if child.text:
                t = libxml2.newText(child.text)
                self.appendNode(nchild, t)
            # Add children
            for c in child:
                for n in self.expandChildElements(c):
                    self.appendNode(nchild, n)
            elements.append(nchild)
            # Add tail
            if child.tail:
                tail = libxml2.newText(child.tail)
                elements.append(tail)
                
            return elements

        def convertElementTree(self, root):
            """ Convert the given tree of etree.Element
                entries to a list of tree nodes for the
                current XML toolkit.
            """
            nroot = self.newNode(root.tag)
            # Copy attributes
            for key, val in root.attrib:
                self.setAttribute(nroot, key, val)
            elements = []
            # Add text
            if root.text:
                t = libxml2.newText(root.text)
                self.appendNode(nroot, t)
            # Add children
            for c in root:
                for n in self.expandChildElements(c):
                    self.appendNode(nroot, n)
            elements.append(nroot)
            # Add tail
            if root.tail:
                tail = libxml2.newText(root.tail)
                elements.append(tail)
                
            return elements

tf = TreeFactory()


class SConsDocTree:
    def __init__(self):
        self.nsmap = {'dbx' : dbxsd}
        self.doc = None
        self.root = None
        self.xpath_context = None

    def parseContent(self, content, include_entities=True):
        """ Parses the given content as XML file. This method
            is used when we generate the basic lists of entities
            for the builders, tools and functions.
            So we usually don't bother about namespaces and resolving
            entities here...this is handled in parseXmlFile below
            (step 2 of the overall process).
        """
        if not include_entities:
            content = remove_entities(content)
        # Create domtree from given content string
        self.root = etree.fromstring(content)

    def parseXmlFile(self, fpath):
        nsmap = {'dbx' : dbxsd}
        if not has_libxml2:
            # Create domtree from file
            domtree = etree.parse(fpath)
            self.root = domtree.getroot()
        else:
            # Read file and resolve entities
            self.doc = libxml2.readFile(fpath, None, libxml2.XML_PARSE_NOENT)
            self.root = self.doc.getRootElement()
            # Create xpath context
            self.xpath_context = self.doc.xpathNewContext()
            # Register namespaces
            for key, val in self.nsmap.iteritems():
                self.xpath_context.xpathRegisterNs(key, val)
            
    def __del__(self):
        if self.doc is not None:
            self.doc.freeDoc()
        if self.xpath_context is not None:
            self.xpath_context.xpathFreeContext()

perc="%"

def validate_all_xml(dpaths, xsdfile=default_xsd):
    xmlschema_context = None
    if not has_libxml2:
        # Use lxml
        xmlschema_context = etree.parse(xsdfile)
    else:
        # Use libxml2 and prepare the schema validation context
        ctxt = libxml2.schemaNewParserCtxt(xsdfile)
        xmlschema_context = ctxt.schemaParse()
        del ctxt
    
    fpaths = []
    for dp in dpaths:
        if dp.endswith('.xml') and isSConsXml(dp):
            path='.'
            fpaths.append(dp)
        else:
            for path, dirs, files in os.walk(dp):
                for f in files:
                    if f.endswith('.xml'):
                        fp = os.path.join(path, f)
                        if isSConsXml(fp):
                            fpaths.append(fp)
                
    fails = []
    for idx, fp in enumerate(fpaths):
        fpath = os.path.join(path, fp)
        print "%.2f%s (%d/%d) %s" % (float(idx+1)*100.0/float(len(fpaths)),
                                     perc, idx+1, len(fpaths),fp)
                                              
        if not tf.validateXml(fp, xmlschema_context):
            fails.append(fp)
            continue

    if has_libxml2:
        # Cleanup
        del xmlschema_context

    if fails:
        return False
    
    return True

class Item(object):
    def __init__(self, name):
        self.name = name
        self.sort_name = name.lower()
        if self.sort_name[0] == '_':
            self.sort_name = self.sort_name[1:]
        self.sets = []
        self.uses = []
        self.summary = None
        self.arguments = None
    def cmp_name(self, name):
        if name[0] == '_':
            name = name[1:]
        return name.lower()
    def __cmp__(self, other):
        return cmp(self.sort_name, other.sort_name)

class Builder(Item):
    pass

class Function(Item):
    def __init__(self, name):
        super(Function, self).__init__(name)

class Tool(Item):
    def __init__(self, name):
        Item.__init__(self, name)
        self.entity = self.name.replace('+', 'X')

class ConstructionVariable(Item):
    pass

class Arguments(object):
    def __init__(self, signature, body=None):
        if not body:
            body = []
        self.body = body
        self.signature = signature
    def __str__(self):
        s = ''.join(self.body).strip()
        result = []
        for m in re.findall('([a-zA-Z/_]+|[^a-zA-Z/_]+)', s):
            if ' ' in m:
                m = '"%s"' % m
            result.append(m)
        return ' '.join(result)
    def append(self, data):
        self.body.append(data)

class SConsDocHandler(object):
    def __init__(self):
        self.builders = {}
        self.functions = {}
        self.tools = {}
        self.cvars = {}

    def parseItems(self, domelem, xpath_context, nsmap):
        items = []

        for i in tf.findAll(domelem, "item", dbxid, xpath_context, nsmap):
            txt = tf.getText(i)
            if txt is not None:
                txt = txt.strip()
                if len(txt):
                    items.append(txt.strip())

        return items

    def parseUsesSets(self, domelem, xpath_context, nsmap):
        uses = []
        sets = []

        for u in tf.findAll(domelem, "uses", dbxid, xpath_context, nsmap):
            uses.extend(self.parseItems(u, xpath_context, nsmap))
        for s in tf.findAll(domelem, "sets", dbxid, xpath_context, nsmap):
            sets.extend(self.parseItems(s, xpath_context, nsmap))
        
        return sorted(uses), sorted(sets)

    def parseInstance(self, domelem, map, Class, 
                        xpath_context, nsmap, include_entities=True):
        name = 'unknown'
        if tf.hasAttribute(domelem, 'name'):
            name = tf.getAttribute(domelem, 'name')
        try:
            instance = map[name]
        except KeyError:
            instance = Class(name)
            map[name] = instance
        uses, sets = self.parseUsesSets(domelem, xpath_context, nsmap)
        instance.uses.extend(uses)
        instance.sets.extend(sets)
        if include_entities:
            # Parse summary and function arguments
            for s in tf.findAllChildrenOf(domelem, "summary", dbxid, xpath_context, nsmap):
                if instance.summary is None:
                    instance.summary = []
                instance.summary.append(tf.copyNode(s))
            for a in tf.findAll(domelem, "arguments", dbxid, xpath_context, nsmap):
                if instance.arguments is None:
                    instance.arguments = []
                instance.arguments.append(tf.copyNode(a))

    def parseDomtree(self, root, xpath_context=None, nsmap=None, include_entities=True):    
        # Process Builders
        for b in tf.findAll(root, "builder", dbxid, xpath_context, nsmap):
            self.parseInstance(b, self.builders, Builder, 
                               xpath_context, nsmap, include_entities)
        # Process Functions
        for f in tf.findAll(root, "scons_function", dbxid, xpath_context, nsmap):
            self.parseInstance(f, self.functions, Function, 
                               xpath_context, nsmap, include_entities)
        # Process Tools
        for t in tf.findAll(root, "tool", dbxid, xpath_context, nsmap):
            self.parseInstance(t, self.tools, Tool, 
                               xpath_context, nsmap, include_entities)
        # Process CVars
        for c in tf.findAll(root, "cvar", dbxid, xpath_context, nsmap):
            self.parseInstance(c, self.cvars, ConstructionVariable, 
                               xpath_context, nsmap, include_entities)
        
    def parseContent(self, content, include_entities=True):
        """ Parses the given content as XML file. This method
            is used when we generate the basic lists of entities
            for the builders, tools and functions.
            So we usually don't bother about namespaces and resolving
            entities here...this is handled in parseXmlFile below
            (step 2 of the overall process).
        """
        # Create doctree
        t = SConsDocTree()
        t.parseContent(content, include_entities)
        # Parse it
        self.parseDomtree(t.root, t.xpath_context, t.nsmap, include_entities)

    def parseXmlFile(self, fpath):
        # Create doctree
        t = SConsDocTree()
        t.parseXmlFile(fpath)
        # Parse it
        self.parseDomtree(t.root, t.xpath_context, t.nsmap)
        
# lifted from Ka-Ping Yee's way cool pydoc module.
def importfile(path):
    """Import a Python source file or compiled file given its path."""
    magic = imp.get_magic()
    file = open(path, 'r')
    if file.read(len(magic)) == magic:
        kind = imp.PY_COMPILED
    else:
        kind = imp.PY_SOURCE
    file.close()
    filename = os.path.basename(path)
    name, ext = os.path.splitext(filename)
    file = open(path, 'r')
    try:
        module = imp.load_module(name, file, path, (ext, 'r', kind))
    except ImportError, e:
        sys.stderr.write("Could not import %s: %s\n" % (path, e))
        return None
    file.close()
    return module

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
