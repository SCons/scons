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

__doc__ = r"""
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
    print("this is example code, it will be offset and indented")
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
    print("this is example code, it will be offset and indented")
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
    print("this is example code, it will be offset and indented")
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
    print("this is example code, it will be offset and indented")
    </example>
    </summary>
    </tool>
"""

import os.path
import re
import sys
import copy
import importlib

try:
    from lxml import etree
except ImportError:
    try:
        import xml.etree.ElementTree as etree
    except ImportError:
        raise ImportError("Failed to import ElementTree from any known place")

# patterns to help trim XML passed in as strings
re_entity = re.compile(r"&([^;]+);")
re_entity_header = re.compile(r"<!DOCTYPE\s+sconsdoc\s+[^\]]+\]>")

# Namespace for the SCons Docbook XSD
dbxsd = "http://www.scons.org/dbxsd/v1.0"
# Namsespace pattern to help identify an scons-xml file read as  bytes
dbxsdpat = b'xmlns="%s"' % dbxsd.encode('utf-8')
# Namespace map identifier for the SCons Docbook XSD
dbxid = "dbx"
# Namespace for schema instances
xsi = "http://www.w3.org/2001/XMLSchema-instance"

# Header comment with copyright
copyright_comment = """
__COPYRIGHT__

This file is processed by the bin/SConsDoc.py module.
See its docstring for a discussion of the format.
"""

def isSConsXml(fpath):
    """ Check whether the given file is an SCons XML file.

    It is SCons XML if it contains the default target namespace definition
    described by dbxsdpat

    """
    try:
        with open(fpath, 'rb') as f:
            content = f.read()
        if content.find(dbxsdpat) >= 0:
            return True
    except Exception:
        pass

    return False

def remove_entities(content):
    # Cut out entity inclusions
    content = re_entity_header.sub("", content, re.M)
    # Cut out entities themselves
    content = re_entity.sub(lambda match: match.group(1), content)

    return content

default_xsd = os.path.join('doc', 'xsd', 'scons.xsd')

ARG = "dbscons"


class Libxml2ValidityHandler:

    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, msg, data):
        if data != ARG:
            raise Exception("Error handler did not receive correct argument")
        self.errors.append(msg)

    def warning(self, msg, data):
        if data != ARG:
            raise Exception("Warning handler did not receive correct argument")
        self.warnings.append(msg)


class DoctypeEntity:
    def __init__(self, name_, uri_):
        self.name = name_
        self.uri = uri_

    def getEntityString(self):
        txt = """    <!ENTITY %(perc)s %(name)s SYSTEM "%(uri)s">
    %(perc)s%(name)s;
""" % {'perc': perc, 'name': self.name, 'uri': self.uri}

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

class TreeFactory:
    def __init__(self):
        pass

    @staticmethod
    def newNode(tag, **kwargs):
        return etree.Element(tag, **kwargs)

    @staticmethod
    def newSubNode(parent, tag, **kwargs):
        return etree.SubElement(parent, tag, **kwargs)

    @staticmethod
    def newEtreeNode(tag, init_ns=False, **kwargs):
        if init_ns:
            NSMAP = {None: dbxsd,
                     'xsi' : xsi}
            return etree.Element(tag, nsmap=NSMAP, **kwargs)

        return etree.Element(tag, **kwargs)

    @staticmethod
    def copyNode(node):
        return copy.deepcopy(node)

    @staticmethod
    def appendNode(parent, child):
        parent.append(child)

    @staticmethod
    def hasAttribute(node, att):
        return att in node.attrib

    @staticmethod
    def getAttribute(node, att):
        return node.attrib[att]

    @staticmethod
    def setAttribute(node, att, value):
        node.attrib[att] = value

    @staticmethod
    def getText(root):
        return root.text
    
    @staticmethod
    def appendCvLink(root, key, lntail):
        linknode = etree.Entity('cv-link-' + key)
        linknode.tail = lntail
        root.append(linknode)

    @staticmethod
    def setText(root, txt):
        root.text = txt

    @staticmethod
    def getTail(root):
        return root.tail

    @staticmethod
    def setTail(root, txt):
        root.tail = txt

    @staticmethod
    def writeGenTree(root, fp):
        dt = DoctypeDeclaration()
        fp.write(etree.tostring(root, encoding="utf-8",
                                pretty_print=True,
                                doctype=dt.createDoctype()).decode('utf-8'))

    @staticmethod
    def writeTree(root, fpath):
        with open(fpath, 'wb') as fp:
            fp.write(etree.tostring(root, encoding="utf-8",
                                    pretty_print=True))

    @staticmethod
    def prettyPrintFile(fpath):
        with open(fpath,'rb') as fin:
            tree = etree.parse(fin)
            pretty_content = etree.tostring(tree, encoding="utf-8", 
                                            pretty_print=True)
    
        with open(fpath,'wb') as fout:
            fout.write(pretty_content)

    @staticmethod
    def decorateWithHeader(root):
        root.attrib["{"+xsi+"}schemaLocation"] = "%s %s/scons.xsd" % (dbxsd, dbxsd)
        return root

    def newXmlTree(self, root):
        """ Return a XML file tree with the correct namespaces set,
            the element root as top entry and the given header comment.
        """
        NSMAP = {None: dbxsd, 'xsi' : xsi}
        t = etree.Element(root, nsmap=NSMAP)
        return self.decorateWithHeader(t)

    # singleton to cache parsed xmlschema..
    xmlschema = None

    @staticmethod
    def validateXml(fpath, xmlschema_context):

        if TreeFactory.xmlschema is None:
            TreeFactory.xmlschema = etree.XMLSchema(xmlschema_context)
        try:
            doc = etree.parse(fpath)
        except Exception as e:
            print("ERROR: %s fails to parse:"%fpath)
            print(e)
            return False
        doc.xinclude()
        try:
            TreeFactory.xmlschema.assertValid(doc)
        except Exception as e:
            print("ERROR: %s fails to validate:" % fpath)
            print(e)
            return False
        return True

    @staticmethod
    def findAll(root, tag, ns=None, xp_ctxt=None, nsmap=None):
        expression = ".//{%s}%s" % (nsmap[ns], tag)
        if not ns or not nsmap:
            expression = ".//%s" % tag
        return root.findall(expression)

    @staticmethod
    def findAllChildrenOf(root, tag, ns=None, xp_ctxt=None, nsmap=None):
        expression = "./{%s}%s/*" % (nsmap[ns], tag)
        if not ns or not nsmap:
            expression = "./%s/*" % tag
        return root.findall(expression)

    @staticmethod
    def convertElementTree(root):
        """ Convert the given tree of etree.Element
            entries to a list of tree nodes for the
            current XML toolkit.
        """
        return [root]

tf = TreeFactory()


class SConsDocTree:
    def __init__(self):
        self.nsmap = {'dbx': dbxsd}
        self.doc = None
        self.root = None
        self.xpath_context = None

    def parseContent(self, content, include_entities=True):
        """ Parses the given text content as XML

        This is the setup portion, called from parseContent in
        an SConsDocHandler instance - see the notes there.
        """
        if not include_entities:
            content = remove_entities(content)
        # Create domtree from given content string
        self.root = etree.fromstring(content)

    def parseXmlFile(self, fpath):
        # Create domtree from file
        parser = etree.XMLParser(load_dtd=True, resolve_entities=False)
        domtree = etree.parse(fpath, parser)
        self.root = domtree.getroot()

    def __del__(self):
        if self.doc is not None:
            self.doc.freeDoc()
        if self.xpath_context is not None:
            self.xpath_context.xpathFreeContext()

perc = "%"

def validate_all_xml(dpaths, xsdfile=default_xsd):
    xmlschema_context = etree.parse(xsdfile)

    fpaths = []
    for dp in dpaths:
        if dp.endswith('.xml') and isSConsXml(dp):
            path = '.'
            fpaths.append(dp)
        else:
            for path, dirs, files in os.walk(dp):
                for f in files:
                    if f.endswith('.xml'):
                        fp = os.path.join(path, f)
                        if isSConsXml(fp):
                            fpaths.append(fp)

    fails = []
    fpaths = sorted(fpaths)
    for idx, fp in enumerate(fpaths):
        fpath = os.path.join(path, fp)
        print("%.2f%s (%d/%d) %s" % (float(idx + 1) * 100.0 /float(len(fpaths)),
                                     perc, idx + 1, len(fpaths), fp))

        if not tf.validateXml(fp, xmlschema_context):
            fails.append(fp)
            continue

    if fails:
        return False

    return True


class Item:
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
    def __eq__(self, other):
        return self.sort_name == other.sort_name
    def __lt__(self, other):
        return self.sort_name < other.sort_name


class Builder(Item):
    pass


class Function(Item):
    pass


class Tool(Item):
    def __init__(self, name):
        Item.__init__(self, name)
        self.entity = self.name.replace('+', 'X')


class ConstructionVariable(Item):
    pass


class Arguments:
    def __init__(self, signature, body=None):
        if not body:
            body = []
        self.body = body
        self.signature = signature
    def __str__(self):
        s = ''.join(self.body).strip()
        result = []
        for m in re.findall(r'([a-zA-Z/_]+|[^a-zA-Z/_]+)', s):
            if ' ' in m:
                m = '"%s"' % m
            result.append(m)
        return ' '.join(result)
    def append(self, data):
        self.body.append(data)


class SConsDocHandler:
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
        """Parse the given content as XML.

        This method is used when we generate the basic lists of entities
        for the builders, tools and functions.  So we usually don't
        bother about namespaces and resolving entities here...
        this is handled in parseXmlFile below (step 2 of the overall process).
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

def importfile(path):
    """Import a Python source file or compiled file given its path."""
    from importlib.util import MAGIC_NUMBER
    with open(path, 'rb') as ifp:
        is_bytecode = MAGIC_NUMBER == ifp.read(len(MAGIC_NUMBER))
    filename = os.path.basename(path)
    name, ext = os.path.splitext(filename)
    if is_bytecode:
        loader = importlib._bootstrap_external.SourcelessFileLoader(name, path)
    else:
        loader = importlib._bootstrap_external.SourceFileLoader(name, path)
    # XXX We probably don't need to pass in the loader here.
    spec = importlib.util.spec_from_file_location(name, path, loader=loader)
    try:
        return importlib._bootstrap._load(spec)
    except ImportError:
        raise Exception(path, sys.exc_info())

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
