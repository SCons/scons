"""SCons.Sig.TimeStamp

The TimeStamp signature package for the SCons software construction
utility.

"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

def current(obj, sig):
    """Return whether the objects timestamp is up-to-date.
    """
    return obj.get_signature() >= sig

def collect(signatures):
    """
    Collect a list of timestamps, returning
    the most-recent timestamp from the list 

    signatures - a list of timestamps
    returns - the most recent timestamp
    """

    if len(signatures) == 0:
        return 0
    elif len(signatures) == 1:
        return signatures[0]
    else:
        return max(signatures)

def signature(obj):
    """Generate a timestamp.
    """
    return obj.get_timestamp()

def to_string(signature):
    """Convert a timestamp to a string"""
    return str(signature)

def from_string(string):
    """Convert a string to a timestamp"""
    return int(string)


