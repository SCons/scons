"""SCons.Sig.MD5

The MD5 signature package for the SCons software construction
utility.

"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import md5
import string



def hexdigest(s):
    """Return a signature as a string of hex characters.
    """
    # NOTE:  This routine is a method in the Python 2.0 interface
    # of the native md5 module, but we want SCons to operate all
    # the way back to at least Python 1.5.2, which doesn't have it.
    h = string.hexdigits
    r = ''
    for c in s:
	i = ord(c)
	r = r + h[(i >> 4) & 0xF] + h[i & 0xF]
    return r



def _init():
    pass	# XXX

def _end():
    pass	# XXX

def current(obj, sig):
    """Return whether a given object is up-to-date with the
    specified signature.
    """
    return obj.signature() == sig

def set():
    pass	# XXX

def invalidate():
    pass	# XXX

def collect(*objects):
    """Collect signatures from a list of objects, returning the
    aggregate signature of the list.
    """
    if len(objects) == 1:
	sig = objects[0].signature()
    else:
	contents = string.join(map(lambda o: o.signature(), objects), ', ')
	sig = signature(contents)
#    if debug:
#	pass
    return sig

def signature(contents):
    """Generate a signature for a byte string.
    """
    return hexdigest(md5.new(contents).digest())

def cmdsig():
    pass	# XXX

def srcsig():
    pass	# XXX
