import os
import stat
import time
import distutils.util


platform = distutils.util.get_platform()

def is_windows():
    """ Check if we're on a Windows platform"""
    if platform.startswith('win'):
        return True
    else:
        return False


def whereis(filename):
    """
    An internal "whereis" routine to figure out if a given program
    is available on this system.
    """
    exts = ['']
    if is_windows():
        exts += ['.exe']
    for dir in os.environ['PATH'].split(os.pathsep):
        f = os.path.join(dir, filename)
        for ext in exts:
            f_ext = f + ext
            if os.path.isfile(f_ext):
                try:
                    st = os.stat(f_ext)
                except:
                    continue
                if stat.S_IMODE(st[stat.ST_MODE]) & 0o111:
                    return f_ext
    return None

# Datestring for debian
# Should look like: Mon, 03 Nov 2016 13:37:42 -0700
deb_date = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())



