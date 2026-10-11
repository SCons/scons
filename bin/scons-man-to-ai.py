#!/usr/bin/env python3
#
# MIT License
#
# Copyright The SCons Foundation
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
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE

"""Generate a token-minimized version of the SCons man page for AI consumption.

The man page is far too large for a language model to read in full: the roff
scons.1 is roughly 230k tokens and the generated HTML about 337k.  This script
emits a compact Markdown reference of roughly 115k tokens which keeps every
documented entry -- each option, tool, builder, function, construction
variable, configure-context method and node attribute, with its description --
while discarding material that costs tokens without informing an AI reader:
markup, cross-reference chrome, code examples, Note blocks and version history.

The input is doc/man/scons.xml, the checked-in DocBook source, so no
documentation build is required.  That file pulls its bulk from the checked-in
doc/generated/*.gen files via XInclude and defines link entities in
doc/generated/*.mod, so both entity resolution and XInclude processing are
needed; this requires lxml (already a development dependency), as the standard
library's ElementTree supports neither.  The generated HTML man page is also
accepted via --input, for comparison against the documentation toolchain.
"""

import argparse
import os
import re
import sys

try:
    import lxml.etree as ET
except ImportError:
    sys.exit(
        "scons-man-to-ai.py: this script requires lxml "
        "(pip install -r requirements-dev.txt)"
    )

# Inline elements naming an identifier.  Rendering these as code spans keeps
# things like $CCFLAGS and --jobs unambiguous once formatting is flattened.
CODEISH = {
    'envar', 'option', 'literal', 'filename', 'function', 'methodname',
    'parameter', 'varname', 'command', 'constant', 'classname', 'code',
    'type', 'userinput', 'computeroutput', 'systemitem', 'replaceable',
    'literal_value',
}

# Illustrative examples: dropped by default, restored with --keep-examples.
# example_commands is SCons' own tag for command examples (rendered as
# <screen> in the HTML), and is by far the largest of the three.
BLOCK_EX = {'example_commands', 'programlisting', 'screen', 'sconstruct',
            'scons_output', 'scons_example'}
# literallayout carries reference data -- the site directory search paths --
# rather than examples, so it is always kept.
BLOCK_KEEP = {'literallayout'}

LIST_TAGS = {'itemizedlist', 'orderedlist', 'simplelist', 'variablelist'}
SECTION_TAGS = ('refsect1', 'refsect2', 'refsect3')
# Block content that may be nested inside a paragraph, and so must not be
# flattened into it.
NESTED_BLOCKS = LIST_TAGS | {'dl', 'ul', 'ol', 'table', 'informaltable'}

# A version-history paragraph ("Changed in version 4.3.0: support for Python
# 3.5 is removed.") is of no use as reference material.  The whole sentence is
# dropped rather than just its label, which would leave a subjectless fragment.
VERSION_NOTE = re.compile(
    r'(?:Changed|New|Deprecated|Removed|Added)\s+in\s+version\s+[0-9][0-9.]*\s*:?'
    # Run to the end of the sentence, but a period between digits (a version
    # or Python release number) does not end it.
    r'(?:[^.!?]|(?<=\d)\.(?=\d)|\.(?=[A-Za-z0-9]))*[.!?]?\s*', re.I)
# A sentence introducing an example reads as dangling once the example is gone.
DANGLING_LEAD = re.compile(r'[^.!?]*:\s*$')
# What survives a pure release-history paragraph is a clause about a retired
# interpreter, not usable reference material.
RELEASE_HISTORY_REMNANT = re.compile(
    r'^The CPython project retired\b|^support for\b.*\bis (?:removed|deprecated)\b',
    re.I)


def norm(s):
    """Collapse whitespace."""
    return ' '.join((s or '').split())


def tag(el):
    """Local name of an element, or None for comments and PIs."""
    if not isinstance(el.tag, str):
        return None
    return ET.QName(el).localname


def kind(el):
    """Classify an element, spanning both the XML and HTML input flavors.

    In the DocBook source the element name carries the meaning; in the
    generated HTML everything is a div/span/p and the class attribute carries
    it.  Normalizing here lets one renderer serve both inputs.
    """
    name = tag(el)
    if name is None:
        return None
    cls = el.get('class')
    if cls and name in ('div', 'span', 'p', 'pre', 'em', 'strong', 'code', 'tt'):
        return cls
    return name


HEADINGS = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')


def title_of(el):
    """Section title: a DocBook <title> child, or the HTML heading/attribute."""
    for child in el:
        if tag(child) in ('title',) + HEADINGS:
            return norm(''.join(child.itertext()))
    return norm(el.get('title'))


def inline(el, drop_examples):
    """Render an element's subtree to compact inline text."""
    k = kind(el)
    if k in BLOCK_EX or k in BLOCK_KEEP:
        if drop_examples and k in BLOCK_EX:
            return ''
        body = ''.join(el.itertext()).strip('\n')
        return '\n```\n' + body.rstrip() + '\n```\n'
    out = []
    if el.text:
        out.append(el.text)
    for child in el:
        out.append(inline(child, drop_examples))
        if child.tail:
            out.append(child.tail)
    text = ''.join(out)
    if k in CODEISH:
        t = norm(text)
        if t and '`' not in t:
            return '`' + t + '`'
    return text


def clean_desc(text, drop_examples=False):
    """Strip version history and example lead-ins from a prose block."""
    text = VERSION_NOTE.sub(' ', text)
    if drop_examples:
        text = DANGLING_LEAD.sub('', text)
    text = norm(text)
    if RELEASE_HISTORY_REMNANT.match(text):
        return ''
    return text


def entries(container):
    """Yield (terms, body-elements) pairs for a definition list.

    Handles the DocBook shape (varlistentry wrapping term/listitem) and the
    HTML shape (a flat run of dt and dd siblings).
    """
    pending_terms, pending_body = [], []
    for el in container:
        k = tag(el)
        if k == 'varlistentry':
            terms = [norm(''.join(c.itertext())) for c in el if tag(c) == 'term']
            body = [c for c in el if tag(c) in ('listitem', 'dd')]
            yield [t for t in terms if t], body
        elif k == 'dt':
            if pending_body:
                yield pending_terms, pending_body
                pending_terms, pending_body = [], []
            pending_terms.append(norm(''.join(el.itertext())))
        elif k == 'dd':
            pending_body.append(el)
    if pending_terms or pending_body:
        yield [t for t in pending_terms if t], pending_body


def render_list(el, drop_examples, drop_notes):
    """Render a definition or bulleted list."""
    # HTML wraps the dl in a div.variablelist; work on the list itself.
    if tag(el) == 'div':
        inner = [c for c in el if tag(c) in ('dl', 'ul', 'ol')]
        if inner:
            el = inner[0]
    if tag(el) in ('variablelist', 'dl'):
        for terms, body in entries(el):
            parts = []
            for item in body:
                parts.extend(blocks(item, drop_examples, drop_notes))
            # Several signatures for one entry (Foo() and env.Foo()) are
            # separate terms in DocBook but one line in the rendered page.
            term = ' '.join(t for t in terms if t)
            body_text = [
                b if b.startswith(('```', '- ', '|')) else clean_desc(b, drop_examples)
                for b in parts
            ]
            body_text = [b for b in body_text if b]
            if not term:
                yield from body_text
                continue
            # The first prose block joins the term line; block-shaped content
            # (examples, lists, tables) has to stay on its own lines.
            if body_text and not body_text[0].startswith(('```', '- ', '|')):
                yield '**' + term + '**: ' + body_text[0]
                rest = body_text[1:]
            else:
                yield '**' + term + '**'
                rest = body_text
            yield from rest
    else:
        for item in el:
            if tag(item) not in ('listitem', 'li', 'member'):
                continue
            text = norm(inline(item, drop_examples))
            if text:
                yield '- ' + text


def render_table(el, drop_examples):
    """Render table rows, collapsing single-column tables to a list."""
    for row in el.iter():
        if tag(row) not in ('row', 'tr'):
            continue
        cells = [norm(inline(c, drop_examples)) for c in row]
        cells = [c for c in cells if c]
        if not cells:
            continue
        # A single-column table is a list; pipes would only add noise.
        if len(cells) == 1:
            yield '- ' + cells[0]
        else:
            yield '| ' + ' | '.join(cells) + ' |'


def scons_version(input_path):
    """Version from SCons/__init__.py, the authoritative source.

    The man page takes its version from doc/version.xml, which is regenerated
    during a build; the checked-in copy names a long-past release, so reading
    it here would stamp the output with the wrong version.
    """
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(input_path)))
    for candidate in (os.path.join(root_dir, 'SCons', '__init__.py'),
                      os.path.join(os.path.dirname(root_dir), 'SCons', '__init__.py')):
        try:
            with open(candidate, encoding='utf-8') as f:
                match = re.search(r'__version__\s*=\s*["\']([^"\']+)', f.read())
        except OSError:
            continue
        if match:
            return match.group(1)
    return ''


def render_synopsis(el):
    """Render a command synopsis, restoring optional/repeat notation.

    DocBook carries "[...]" and "..." as attributes on <arg> rather than as
    text, so the plain text of the element would read "scons options targets".
    """
    if tag(el) != 'cmdsynopsis':
        found = [c for c in el.iter() if tag(c) == 'cmdsynopsis']
        if not found:
            # HTML: the synopsis is already rendered, minus its heading.
            return norm(' '.join(''.join(c.itertext()) for c in el
                                 if tag(c) not in HEADINGS))
        el = found[0]
    parts = []
    for child in el:
        text = norm(''.join(child.itertext()))
        if not text:
            continue
        if tag(child) == 'arg':
            if child.get('choice', 'opt') == 'opt':
                text = '[' + text + ']'
            if child.get('rep') == 'repeat':
                text += '...'
        parts.append(text)
    return ' '.join(parts)


def blocks(container, drop_examples, drop_notes):
    """Yield markdown blocks for the content of a container element."""
    for el in container:
        k = kind(el)
        if k is None or k == 'title' or tag(el) in HEADINGS:
            continue
        if drop_notes and k == 'note':
            continue
        if k in BLOCK_EX or k in BLOCK_KEEP:
            body = inline(el, drop_examples)
            if body.strip():
                yield body.strip()
        elif k in LIST_TAGS or k in ('dl', 'ul', 'ol'):
            yield from render_list(el, drop_examples, drop_notes)
        elif k in ('table', 'informaltable'):
            yield from render_table(el, drop_examples)
        elif k in SECTION_TAGS:
            continue  # handled by walk()
        elif k in ('note', 'blockquote', 'example', 'informalexample'):
            yield from blocks(el, drop_examples, drop_notes)
        elif any(kind(c) in NESTED_BLOCKS for c in el):
            # A para can wrap a nested list or table (Decider's mode values,
            # for instance).  Flattening it inline would swallow those
            # entries, so emit the paragraph's own lead-in text and then let
            # each child render as its own block.
            lead = norm(el.text)
            if lead:
                yield lead
            yield from blocks(el, drop_examples, drop_notes)
        else:
            text = inline(el, drop_examples)
            # inline() splices fenced blocks into the stream; keep them whole
            # and normalize only the prose around them.
            for part in re.split(r'\n(?=```)|(?<=```)\n', text):
                out = part.strip() if part.strip().startswith('```') else norm(part)
                if out:
                    yield out


def walk(section, level, out, drop_examples, drop_notes):
    """Emit a section heading, its own content, then its subsections."""
    title = title_of(section)
    if title:
        out.append('\n' + '#' * level + ' ' + title + '\n')
    for block in blocks(section, drop_examples, drop_notes):
        if block.startswith(('```', '**', '- ', '|')):
            out.append(block)
        else:
            cleaned = clean_desc(block, drop_examples)
            if cleaned:
                out.append(cleaned)
    for child in section:
        if kind(child) in SECTION_TAGS:
            walk(child, level + 1, out, drop_examples, drop_notes)


def parse(path):
    """Parse the man page source, resolving entities and XIncludes."""
    parser = ET.XMLParser(load_dtd=True, resolve_entities=True, no_network=True,
                          huge_tree=True, recover=True)
    if path.lower().endswith(('.html', '.htm')):
        tree = ET.parse(path, ET.HTMLParser(huge_tree=True, recover=True))
        return tree.getroot()
    # Entity and XInclude hrefs in scons.xml are relative to its own
    # directory, so parse from there to keep the script cwd-independent.
    cwd = os.getcwd()
    directory, name = os.path.split(os.path.abspath(path))
    try:
        os.chdir(directory)
        tree = ET.parse(name, parser)
        tree.xinclude()
    finally:
        os.chdir(cwd)
    return tree.getroot()


def find_all(root, names):
    """All elements matching names, in document order.

    Matches the element name (DocBook) or the class attribute (HTML).
    """
    return [el for el in root.iter() if tag(el) in names or kind(el) in names]


def main():
    parser = argparse.ArgumentParser(
        description='Generate a token-minimized SCons man page for AI consumption.')
    parser.add_argument('-i', '--input', default='doc/man/scons.xml',
                        help='DocBook source (default: %(default)s); '
                             'a generated .html man page is also accepted')
    parser.add_argument('-o', '--output', default='-',
                        help='output file, or - for stdout (default: -)')
    parser.add_argument('--keep-examples', action='store_true',
                        help='retain code examples (default: drop them)')
    parser.add_argument('--keep-notes', action='store_true',
                        help='retain Note blocks (default: drop them)')
    args = parser.parse_args()

    root = parse(args.input)
    drop_examples = not args.keep_examples
    drop_notes = not args.keep_notes

    version = scons_version(args.input)
    if not version:
        for el in find_all(root, {'releaseinfo', 'p'}):
            if tag(el) == 'releaseinfo' or el.get('class') == 'releaseinfo':
                version = norm(''.join(el.itertext()))
                break

    out = [
        '# SCons man page (%s) - condensed reference' % version if version
        else '# SCons man page - condensed reference',
        '',
        'Machine-oriented condensation of the scons(1) man page: every option, tool, '
        'builder, function and construction variable is retained with its description; '
        'man-page formatting, cross-reference chrome and version-history notes are '
        'removed.',
    ]

    for el in find_all(root, {'refnamediv'}):
        parts = [norm(''.join(c.itertext())) for c in el
                 if tag(c) in ('refname', 'refpurpose')]
        parts = [p for p in parts if p]
        if not parts:  # HTML: a heading followed by the description
            parts = [norm(''.join(c.itertext())) for c in el
                     if tag(c) not in HEADINGS and norm(''.join(c.itertext()))]
        out.append('\n**Name**: ' + ' - '.join(parts))
        break
    for el in find_all(root, {'cmdsynopsis', 'refsynopsisdiv'}):
        synopsis = render_synopsis(el)
        if synopsis:
            out.append('**Synopsis**: `' + synopsis + '`')
            break

    for section in root.iter():
        if kind(section) == 'refsect1':
            walk(section, 2, out, drop_examples, drop_notes)

    text = '\n'.join(out)
    text = re.sub(r'\n{3,}', '\n\n', text).strip() + '\n'

    if args.output == '-':
        sys.stdout.write(text)
    else:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f'wrote {args.output}: {len(text):,} chars', file=sys.stderr)


if __name__ == '__main__':
    main()
