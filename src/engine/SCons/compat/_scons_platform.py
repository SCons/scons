#
# __COPYRIGHT__
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__doc__ = """
platform backwards-compatibility module for older (pre-2.3) Python versions

This does not not NOT (repeat, *NOT*) provide complete platform
functionality.  It only wraps the portions of platform functionality used
by SCons.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

### Portable uname() interface

_uname_cache = None

def uname():

    """ Fairly portable uname interface. Returns a tuple
        of strings (system,node,release,version,machine,processor)
        identifying the underlying platform.

        Note that unlike the os.uname function this also returns
        possible processor information as an additional tuple entry.

        Entries which cannot be determined are set to ''.

    """
    global _uname_cache
    no_os_uname = 0

    if _uname_cache is not None:
        return _uname_cache

    processor = ''

    # Get some infos from the builtin os.uname API...
    try:
        system,node,release,version,machine = os.uname()
    except AttributeError:
        no_os_uname = 1

    if no_os_uname or not filter(None, (system, node, release, version, machine)):
        # Hmm, no there is either no uname or uname has returned
        #'unknowns'... we'll have to poke around the system then.
        if no_os_uname:
            system = sys.platform
            release = ''
            version = ''
            node = _node()
            machine = ''

        use_syscmd_ver = 01

        # Try win32_ver() on win32 platforms
        if system == 'win32':
            release,version,csd,ptype = win32_ver()
            if release and version:
                use_syscmd_ver = 0
            # Try to use the PROCESSOR_* environment variables
            # available on Win XP and later; see
            # http://support.microsoft.com/kb/888731 and
            # http://www.geocities.com/rick_lively/MANUALS/ENV/MSWIN/PROCESSI.HTM
            if not machine:
                machine = os.environ.get('PROCESSOR_ARCHITECTURE', '')
            if not processor:
                processor = os.environ.get('PROCESSOR_IDENTIFIER', machine)

        # Try the 'ver' system command available on some
        # platforms
        if use_syscmd_ver:
            system,release,version = _syscmd_ver(system)
            # Normalize system to what win32_ver() normally returns
            # (_syscmd_ver() tends to return the vendor name as well)
            if system == 'Microsoft Windows':
                system = 'Windows'
            elif system == 'Microsoft' and release == 'Windows':
                # Under Windows Vista and Windows Server 2008,
                # Microsoft changed the output of the ver command. The
                # release is no longer printed.  This causes the
                # system and release to be misidentified.
                system = 'Windows'
                if '6.0' == version[:3]:
                    release = 'Vista'
                else:
                    release = ''

        # In case we still don't know anything useful, we'll try to
        # help ourselves
        if system in ('win32','win16'):
            if not version:
                if system == 'win32':
                    version = '32bit'
                else:
                    version = '16bit'
            system = 'Windows'

        elif system[:4] == 'java':
            release,vendor,vminfo,osinfo = java_ver()
            system = 'Java'
            version = string.join(vminfo,', ')
            if not version:
                version = vendor

        elif os.name == 'mac':
            release,(version,stage,nonrel),machine = mac_ver()
            system = 'MacOS'

    # System specific extensions
    if system == 'OpenVMS':
        # OpenVMS seems to have release and version mixed up
        if not release or release == '0':
            release = version
            version = ''
        # Get processor information
        try:
            import vms_lib
        except ImportError:
            pass
        else:
            csid, cpu_number = vms_lib.getsyi('SYI$_CPU',0)
            if (cpu_number >= 128):
                processor = 'Alpha'
            else:
                processor = 'VAX'
    if not processor:
        # Get processor information from the uname system command
        processor = _syscmd_uname('-p','')

    #If any unknowns still exist, replace them with ''s, which are more portable
    if system == 'unknown':
        system = ''
    if node == 'unknown':
        node = ''
    if release == 'unknown':
        release = ''
    if version == 'unknown':
        version = ''
    if machine == 'unknown':
        machine = ''
    if processor == 'unknown':
        processor = ''

    #  normalize name
    if system == 'Microsoft' and release == 'Windows':
        system = 'Windows'
        release = 'Vista'

    _uname_cache = system,node,release,version,machine,processor
    return _uname_cache

### Direct interfaces to some of the uname() return values

def system():

    """ Returns the system/OS name, e.g. 'Linux', 'Windows' or 'Java'.

        An empty string is returned if the value cannot be determined.

    """
    return uname()[0]

def node():

    """ Returns the computer's network name (which may not be fully
        qualified)

        An empty string is returned if the value cannot be determined.

    """
    return uname()[1]

def release():

    """ Returns the system's release, e.g. '2.2.0' or 'NT'

        An empty string is returned if the value cannot be determined.

    """
    return uname()[2]

def version():

    """ Returns the system's release version, e.g. '#3 on degas'

        An empty string is returned if the value cannot be determined.

    """
    return uname()[3]

def machine():

    """ Returns the machine type, e.g. 'i386'

        An empty string is returned if the value cannot be determined.

    """
    return uname()[4]

def processor():

    """ Returns the (true) processor name, e.g. 'amdk6'

        An empty string is returned if the value cannot be
        determined. Note that many platforms do not provide this
        information or simply return the same value as for machine(),
        e.g.  NetBSD does this.

    """
    return uname()[5]

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
