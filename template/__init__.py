"""${subst '/' '.' ${subst '^src/' '' ${subst '/[^/]*$' '' $filename}}}

XXX

"""

__revision__ = "${subst '^src/scons/' '' $filename} __REVISION__ __DATE__ __DEVELOPER__"

__version__ = "__VERSION__"
