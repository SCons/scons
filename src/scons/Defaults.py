"""scons.Defaults

Builders and other things for the local site.  Here's where we'll
duplicate the functionality of autoconf until we move it into the
installation procedure or use something like qmconf.

"""

__revision__ = "local.py __REVISION__ __DATE__ __DEVELOPER__"



from scons.Builder import Builder



Object = Builder(name = 'Object', action = 'cc -c -o %(target)s %(source)s')
Program = Builder(name = 'Program', action = 'cc -o %(target)s %(source)s')

Builders = [Object, Program]
