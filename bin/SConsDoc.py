#!/usr/bin/env python
#
# Module for handling SCons documentation processing.
#
import os.path
import imp
import sys
import xml.sax.handler

class Item:
    def __init__(self, name):
        self.name = name
        self.sort_name = name.lower()
        if self.sort_name[0] == '_':
            self.sort_name = self.sort_name[1:]
        self.summary = []
        self.uses = None
    def cmp_name(self, name):
        if name[0] == '_':
            name = name[1:]
        return name.lower()
    def __cmp__(self, other):
        return cmp(self.sort_name, other.sort_name)

class Builder(Item):
    pass

class Tool(Item):
    def __init__(self, name):
        Item.__init__(self, name)
        self.entity = self.name.replace('+', 'X')

class ConstructionVariable(Item):
    pass

class Chunk:
    def __init__(self, tag, body=None):
        self.tag = tag
        if not body:
            body = []
        self.body = body
    def __str__(self):
        body = ''.join(self.body)
        return "<%s>%s</%s>\n" % (self.tag, body, self.tag)
    def append(self, data):
        self.body.append(data)

class Summary:
    def __init__(self):
        self.body = []
        self.collect = []
    def append(self, data):
        self.collect.append(data)
    def end_para(self):
        text = ''.join(self.collect)
        paras = text.split('\n\n')
        if paras == ['\n']:
            return
        if paras[0] == '':
            self.body.append('\n')
            paras = paras[1:]
            paras[0] = '\n' + paras[0]
        if paras[-1] == '':
            paras = paras[:-1]
            paras[-1] = paras[-1] + '\n'
            last = '\n'
        else:
            last = None
        sep = None
        for p in paras:
            c = Chunk("para", p)
            if sep:
                self.body.append(sep)
            self.body.append(c)
            sep = '\n'
        if last:
            self.body.append(last)
    def begin_chunk(self, chunk):
        self.end_para()
        self.collect = chunk
    def end_chunk(self):
        self.body.append(self.collect)
        self.collect = []

class SConsDocHandler(xml.sax.handler.ContentHandler,
                      xml.sax.handler.ErrorHandler):
    def __init__(self):
        self._start_dispatch = {}
        self._end_dispatch = {}
        keys = self.__class__.__dict__.keys()
        start_tag_method_names = filter(lambda k: k[:6] == 'start_', keys)
        end_tag_method_names = filter(lambda k: k[:4] == 'end_', keys)
        for method_name in start_tag_method_names:
            tag = method_name[6:]
            self._start_dispatch[tag] = getattr(self, method_name)
        for method_name in end_tag_method_names:
            tag = method_name[4:]
            self._end_dispatch[tag] = getattr(self, method_name)
        self.stack = []
        self.collect = []
        self.current_object = []
        self.builders = {}
        self.tools = {}
        self.cvars = {}

    def startElement(self, name, attrs):
        try:
            start_element_method = self._start_dispatch[name]
        except KeyError:
            self.characters('<%s>' % name)
        else:
            start_element_method(attrs)

    def endElement(self, name):
        try:
            end_element_method = self._end_dispatch[name]
        except KeyError:
            self.characters('</%s>' % name)
        else:
            end_element_method()

    #
    #
    def characters(self, chars):
        self.collect.append(chars)

    def begin_collecting(self, chunk):
        self.collect = chunk
    def end_collecting(self):
        self.collect = []

    def begin_chunk(self):
        pass
    def end_chunk(self):
        pass

    #
    #
    #

    def begin_xxx(self, obj):
        self.stack.append(self.current_object)
        self.current_object = obj
    def end_xxx(self):
        self.current_object = self.stack.pop()

    #
    #
    #
    def start_scons_doc(self, attrs):
        pass
    def end_scons_doc(self):
        pass

    def start_builder(self, attrs):
        name = attrs.get('name')
        try:
            builder = self.builders[name]
        except KeyError:
            builder = Builder(name)
            self.builders[name] = builder
        self.begin_xxx(builder)
    def end_builder(self):
        self.end_xxx()

    def start_tool(self, attrs):
        name = attrs.get('name')
        try:
            tool = self.tools[name]
        except KeyError:
            tool = Tool(name)
            self.tools[name] = tool
        self.begin_xxx(tool)
    def end_tool(self):
        self.end_xxx()

    def start_cvar(self, attrs):
        name = attrs.get('name')
        try:
            cvar = self.cvars[name]
        except KeyError:
            cvar = ConstructionVariable(name)
            self.cvars[name] = cvar
        self.begin_xxx(cvar)
    def end_cvar(self):
        self.end_xxx()

    def start_summary(self, attrs):
        summary = Summary()
        self.current_object.summary = summary
        self.begin_xxx(summary)
        self.begin_collecting(summary)
    def end_summary(self):
        self.current_object.end_para()
        self.end_xxx()

    def start_example(self, attrs):
        example = Chunk("programlisting")
        self.current_object.begin_chunk(example)
    def end_example(self):
        self.current_object.end_chunk()

    def start_uses(self, attrs):
        self.begin_collecting([])
    def end_uses(self):
        self.current_object.uses = ''.join(self.collect).split()
        self.end_collecting()

    # Stuff for the ErrorHandler portion.
    def error(self, exception):
        linenum = exception._linenum - self.preamble_lines
        sys.stderr.write('%s:%d:%d: %s (error)\n' % (self.filename, linenum, exception._colnum, ''.join(exception.args)))

    def fatalError(self, exception):
        linenum = exception._linenum - self.preamble_lines
        sys.stderr.write('%s:%d:%d: %s (fatalError)\n' % (self.filename, linenum, exception._colnum, ''.join(exception.args)))

    def set_file_info(self, filename, preamble_lines):
        self.filename = filename
        self.preamble_lines = preamble_lines

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
