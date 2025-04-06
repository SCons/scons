.. SCons documentation master file, originally created by
   sphinx-quickstart on Mon Apr 30 09:36:53 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SCons API Documentation
=======================

.. Attention::
   This is the **internal** API Documentation for SCons (aka
   "everything"). It is generated automatically from code docstrings using
   the `Sphinx <https://www.sphinx-doc.org>`_ documentation generator.

   Any missing/incomplete information is due to shortcomings in the
   docstrings in the code. To not be too flippant about it, filling
   in all the docstrings has not always been a priority across the
   two-plus decades SCons has been in existence (contributions on this
   front are welcomed).  Additionally, for SCons classes which inherit
   from Python standard library classes (such as ``UserList``,
   ``UserDict``, ``UserString``), the generated pages will show methods
   that are inherited, sometimes with no information at all, sometimes
   with a signature/description that seems mangled: Python upstream has
   similar limitations as to the quality of dosctrings vs the current
   standards Sphinx expects.  Inherited interfaces from outside SCons
   code can be identified by the lack of a ``[source]`` button to the
   right of the method signature.

   If you are looking for the Public API - the interfaces that have
   long-term consistency guarantees, which you can reliably use when
   writing a build system for a project - see the `SCons Reference Manual
   <https://scons.org/doc/production/HTML/scons-man.html>`_.  Note that
   what is Public API and what is not is not clearly delineated in these
   API Docs.

   The target audience is both developers contributing to SCons itself,
   and those writing external Tools, Builders, and other related
   functionality for their project, who may need to reach beyond the
   Public API to accomplish their tasks. Reaching into internals is fine,
   but comes with the usual risks of "things here could change, it's up
   to you to keep your code working".


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   SCons
   SCons.compat
   SCons.Node
   SCons.Platform
   SCons.Scanner
   SCons.Script
   SCons.Taskmaster
   SCons.Tool
   SCons.Util
   SCons.Variables


Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
