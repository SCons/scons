"""SCons.Defaults

Builders and other things for the local site.  Here's where we'll
duplicate the functionality of autoconf until we move it into the
installation procedure or use something like qmconf.

"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"



import SCons.Builder



Object = SCons.Builder.Builder(name = 'Object',
				action = 'cc -c -o %(target)s %(source)s')
Program = SCons.Builder.Builder(name = 'Program',
				action = 'cc -o %(target)s %(source)s')

Builders = [Object, Program]
