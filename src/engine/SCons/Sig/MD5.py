"""SCons.Sig.MD5

The MD5 signature package for the SCons software construction
utility.

"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import md5
import string

def current(obj, sig):
    """Return whether a given object is up-to-date with the
    specified signature.
    """
    return obj.get_signature() == sig

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

def collect(signatures):
    """
    Collect a list of signatures into an aggregate signature.

    signatures - a list of signatures
    returns - the aggregate signature
    """
    if len(signatures) == 1:
	return signatures[0]
    else:
        contents = string.join(signatures, ', ')
	return hexdigest(md5.new(contents).digest())

def signature(obj):
    """Generate a signature for an object
    """
    return hexdigest(md5.new(obj.get_contents()).digest())

def to_string(signature):
    """Convert a signature to a string"""
    return signature

def from_string(string):
    """Convert a string to a signature"""
    return string
