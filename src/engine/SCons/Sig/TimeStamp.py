"""SCons.Sig.TimeStamp

The TimeStamp signature package for the SCons software construction
utility.

"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

def _init():
    pass	# XXX

def _end():
    pass	# XXX

def current(obj, sig):
    """Return whether the object's timestamp is up-to-date.
    """
    return obj.signature() >= sig

def set():
    pass	# XXX

def invalidate():
    pass	# XXX

def collect(*objects):
    """Collect timestamps from a list of objects, returning
    the most-recent timestamp from the list.
    """
    r = 0
    for obj in objects:
	s = obj.signature()
	if s > r:
	    r = s
    return r

def signature(contents):
    """Generate a timestamp.
    """
    pass	# XXX
#    return md5.new(contents).hexdigest()	# 2.0
    return hexdigest(md5.new(contents).digest())

def cmdsig():
    pass	# XXX

def srcsig():
    pass	# XXX
