=============================
SCons Documentation Toolchain
=============================


Introduction
============

This is an overview of the current SCons documentation toolchain.
As a prospective doc editor, you should be able to quickly
understand the basic concepts (if not, please let the project know how
it falls short).  It is also a reference for core developers and the
release team.

.. image:: images/overview.png

The diagram above roughly shows the steps that we currently use.
Note there are two separate sets of documentation maintained with
the project code itself: the reference manual and user guide,
which have xml source files; and the docstrings in the Python code,
from which the API documentation is generated. Most of the time
when we talk about "SCons Documentation" we mean the former,
as that's what is intended for end-user consumption.

If you look at the diagram, it looks a bit complicated. after
reading this overview, it will be clear what is actually happening,
and why we need all these steps.

Our toolchain doesn't only produce HTML and PDF files that are nice
to look at, it also performs a lot of processing under the covers. We
try to have our documentation as consistent as possible to the current
behaviour of the source code, but this requires some extra steps.

So let's start right at the top...

Writer's view
=============

SCons documentation is written in Docbook XML.
The toolchain is set up so a writer has a restricted view of the
whole "document processing thingy". All you should need to be concerned
with is to edit existing text or write new sections and paragraphs.
Sometimes even a completely new chapter has to be added. The hope
is that you can fire up your XML editor of choice and type away.

XML is easy to get wrong, so you need to care about
validating the XML files
against our special "SCons Docbook DTD/XSD".
If you're not using an XML editor, validate by

::

    python bin/docs-validate.py


from the top source folder. If you are able to use
an XML editor, many of the potential problems are avoided,
as it will complain real-time.
The most common error is not matching tag opening and closing
(for example ``<tag>foo<tag>`` is an easy typing error to make,
as is starting a ``<para>``, typing text, and not adding the
closing ``</para>``, as is mistyping one of the two
tag markers). XML editors make it much harder to make
those errors, which, minor though they seem, will completely
break the document build. Unfortunately, the validation tools
(which rely on the capabilities of the XML parser in use)
are not that hard to fool, so you may get errors which are
not that easy to deciper. There isn't much we can do about that.

Everything's looking okay, all validation passed? Good, then simply
commits your new work, and create a pull request on Github. That's it!

Additionally, you can create the single documents locally if you want
to get a feel for how the final result looks (and who doesn't?). Each of
the document folders (``design``, ``developer``, ``man``, ``python10``,
``reference``, and ``user``) contains an ``SConstruct`` file along with
the actual XML files. You can call

::

    python ../../scripts/scons.py

from within the directory, and have the MAN pages or HTML created...even
PDF, if you have a renderer installed (``fop``, ``xep`` or ``jw``).
At least ``fop`` doesn't like everything the docbook/xml chain
produces and will spew a lot of errors, which we *think* are harmless.

Validation
==========

Just a few more words about the validation step.  We are using our
own DTD/XSD as a kind of hook, which only exists to link our own SCons
documentation tags into the normal Docbook XSD. For the output, we always
have an intermediary step (see diagram above), where we rewrite tags like
``cvar`` into a block of Docbook formatting elements representing it.

The toolchain, and all the Python scripts supporting it, are based
on the prerequisite that all documents are valid against the SCons
Docbook XSD. This step guarantees that we can accept the pull request
of a user/writer with all his changes, and can create the documentation
for a new release of SCons without any problems at a later time.


Entities
========

We are using entities for special keywords like ``SCons`` that should
appear with the same formatting throughout the text. This allows a
single place to make styling changes if needed. These are kept in
a single file ``doc/scons.mod`` which gets included by the documents,
and can be used anywhere in the documentation files.

Additionally, for the definitions of the four special types available
in the SCons doctype - Tool, Builder, Construction Variable and Function -
a bunch of reference links in the form of entities are generated.
These entities can be used in the MAN page and the User manual.
Note that the four type tags themselves (``<tool>``, ``<builder>``,
``<cvar>`` and ``<function>``) can only be used in documentation
sources in the ``SCons`` directory; the build will not scan for these
tags in files in the ``doc`` directory.

When you add tool documentation using the ``<tool>`` tag,
let's say for a tool named ``foobar``, you can use the two
automatically generated entities

*t-foobar*
    which prints the name of the Tool, and

*t-link-foobar*
    which is a link to the description of the Tool

The link will be to the appropriate Appendix in the User Guide,
or to the proper section in the manpage.

The ``<builder>`` tag similarly generates entities with the *b-* prefix,
the ``<function>`` tag generates entities with the *f-* prefix,
and the ``<cvar>`` tag generates entities with the *cv-* prefix.

In the case of Functions, there may be pairs of these, depending
on the value of the signature attribute: this attribute tells
whether only the global function form, or only the environment
method form, or both, exist. If all four exist you will get:

*f-foobar*
    which prints the name of the global Function

*f-env-foobar*
    which prints the name of the environment method

*f-link-foobar*
    which is a link to the description of the global Function

*f-link-env-foobar*
    which is a link to the description of the environment method


By calling the script

::

    python bin/docs-update-generated.py

you can recreate the lists of entities (``*.mod``) in the ``generated``
folder.  At the same time, this will generate the matching ``*.gen``
files, which hold the full descriptions of all the Builders, Tools,
Functions and CVars for the MAN page and the User Guide's appendix.
Thus, you want to regenerate when there's a change to
any of those four special elements, or an added or deleted element.
These generated files are left checked in so in the normal case you
can just rebuild the docs without having to first generate the entity
files.

For more information about how to properly describe these elements,
refer to the start of the Python script ``bin/SConsDoc.py``. It explains
the available tags and the exact syntax in detail.


Linking
=======

Normal Docbook (v4.5 style, as of this writing) in-document linking
is supported, as is linking to documents with a web address.
For any element in a document, you can include an ``id=name``
attribute to set an identifier, and write a link to that identifier.
Many of the section headings already have such identifiers,
and it is fine to add more, as long as they remain unique.
As noted in the previous section, for the special types,
entities are generated which contain links,
so you can just use those entities instead
of writing the link reference manually.

There is something to keep in mind about linking, however.
Cross-document links between the MAN page and the User Guide
do not work.  But some text is shared between the two, which
allows the appearance of such linking, and this is where it
gets a little confusing.  The text defined by the four special
types is generated into the ``*.gen`` files,
which get included both in the appropriate places in the MAN page,
and in the Appendix in the User Guide.  Using entities within
this shared content is fine.  Writing links in this shared
content to element identifiers defined elsewhere is not.

That sounds a little confusing so here is a real example:
an xml source file in ``SCons`` defines the ``SCANNERS``
construction variable by using ``<cvar name="SCANNERS"> ... </cvar>``.
This will generate the linking entity ``&cv-link-SCANNERS;``,
which can be used anywhere the ``doc/generated/variables.gen``
file is included (i.e. MAN page and User Guide for now)
to leave a link to this definition.
But the text written inside the ``SCANNERS`` definition
also wants to refer to the "Builder Objects" and "Scanner
Objects" sections in the MAN page, as this contains relevant
further description. This reference should not include an
XML link, even though the MAN page defines the two identifiers
``scanner_objects`` and ``builder_objects``, because this
definition will *also* be included in the User Guide, which
has no such section names or identifiers.  It is better here
to write it all in text, as in *See the manpage section
"Builder Objects"* than to leave a dangling reference in one
of the docs.

Context
=======
While it is very convenient to document related
things together in one xml file, and this is encouraged
as it helps writers keep things in sync,
be aware the information recorded inside the four special tags
will not be presented together in the output documents.
For example, when documenting a Tool in
``SCons/Tool/newtool.xml`` using the ``<tool>`` tag,
and noting that the tool ``<uses>`` or ``<sets>``
certain construction variables,
those construction variables can be documented
right there as well using ``<cvar>`` tags.
When processed with ``SConsDoc`` module,
this will generate xml from the
``<tool>`` tag into the ``tools.{gen,mod}`` files,
and xml from the ``<cvar>`` tag into
the ``variables.{gen,mod}`` files;
those files are then included each into their own
section, so the entries may end up separated by
hundreds of lines in the final output.
The special entries will also be sorted in their
own sections, which might cause two entries using the
same tag in the same source file to be separated.
All this to say: do not write your doc text
with the idea that the locality you see in the xml source file
will be preserved when consumed in a web browser,
manpage viewer, PDF file, etc. Provide sufficient context
so entries can stand on their own.

Another quirk is that ``SConsDoc``
will take all occurrences of a special tag and
combine those contents into a single entry in the generated file.
As such, normally there should be only one definition of
each element project-wide. This particularly comes up in tool definitions,
as several tools may refer to the same construction variable.
It is suggested to pick one file to write the documentation in,
and then in the other tool documents referencing it,
place a comment indicating which file the variable is documented in -
this will keep future editors from having to hunt too far for it.

SCons Examples
==============

In the User Guide, we support automatically created examples. This
means that the output of the specified source files and SConstructs
is generated by running them with the current SCons version.  We do this
to ensure that the output displayed in the manual is identical to what
you get when you run the example on the command-line, without having
to remember to manually update the example outputs all the time.

A short description about how these examples have to be defined can be
found at the start of the file ``bin/SConsExamples.py``. Call

::

    python bin/docs-create-example-outputs.py

from the top level source folder, to run all examples through SCons.

Before this script starts to generate any output, it checks whether the
names of all defined examples are unique. Another important prerequisite
is that for every example all the single ``scons_output`` blocks need
to have a ``suffix`` attribute defined. These suffixes also have to be
unique, within each example, as this controls the ordering.

All example output files (``*.xml``) get written to the folder
``doc/generated/examples``, together with all files defined via the
``scons_example_file`` tag. They are put under version control, in
part so that the version control system can show any unexpected
changes in the outputs after editing the docs:

::

   git diff doc/generated/examples

Some of the changes in example text are phony: despite best
efforts to eliminate system-specifics, sometimes they leak through.
There is at least one example that gets the pathname to the
build directory of the machine the example is generated on.

Note that these output files are not actually needed for editing the
documents. When loading the User manual into an XML editor, you will
always see the example's definition. Only when you create some output,
the files from ``doc/generated/examples`` get XIncluded and all special
``scons*`` tags are transformed into Docbook elements.


Directories
===========

Documents are in the folders ``design``, ``developer``, ``man``,
``python10``, ``reference``, and ``user``. Note that of these,
only ``man`` and ``user`` are actively maintained and some of
the others are vastly out of date.  If submitting a github
Pull Request for a new SCons feature, you will only be required
to update the documentation that goes into the manpage and the
User Guide.

*editor_configs*
    Prepared configuration sets for the validating WYSIWYG XML editors
    XmlMind and Serna. You'll probably want to try the latter, because
    the XXE config requires you to have a full version (costing a few
    hundred bucks) and is therefore untested. For installing the Serna
    config, simply copy the ``scons`` folder into the ``plugins``
    directory of your installation. Likewise, the XXE files from the
    ``xmlmind`` folder have to be copied into ``~/.xxe4/`` under Linux.

*generated*
    Entity lists and outputs of the UserGuide examples. They get generated
    by the update scripts ``bin/docs-update-generated.py``
    and ``bin/docs-create-example-outputs.py``.

*images*
    Images for the ``overview.rst`` document.

*xsd*
    The SCons Docbook schema (XSD), based on the Docbook v4.5 DTD/XSD.

*xslt*
    XSLT transformation scripts for converting the special SCons
    tags like ``scons_output`` to valid Docbook during document
    processing.

