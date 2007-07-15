"""SCons.Tool.Packaging.packager
"""

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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import SCons.Defaults
from SCons.Util import strip_abs_path

class Packager:
    """ abstract superclass of all packagers.

    Defines the minimal set of function which need to be implemented in order
    to create a new packager.
    """
    def __init__(self):
        self.specfile_suffix = '.spec'

    def create_builder(self, env, kw):
        raise Exception( "%s does not implement create_builder()" % (self.__class__.__name_) )

    def add_targets(self, kw):
        """ In the absence of a target this method creates a default one of
        the spec given in the kw argument.
        """
        if not kw.has_key('target'):
            NAME, VERSION = kw['projectname'], kw['version']
            kw['target'] = [ "%s-%s"%(NAME,VERSION) ]

        return kw

    def strip_install_emitter(self, target, source, env):
        """ this emitter assert that all files in source have an InstallBuilder
        attached. We take their sources and copy over the file tags, so the
        the builder this emitter is attached to is independent of the *installed*
        files.
        """
        tag_factories = [ LocationTagFactory() ]

        def has_no_install_location(file):
            return not ( file.has_builder() and (file.builder.name == 'InstallBuilder' or file.builder.name == 'InstallAsBuilder') )

        # check if all source file belong into this package.
        files = filter( has_no_install_location, source )
        if len( files ) != 0:
            raise SCons.Errors.UserError( "There are files which have no Install() Builder attached and are therefore not packageable\n%s" % map( lambda x: x.get_path(), files ) )

        # All source files have an InstallBuilder attached and we don't want our
        # package to be dependent on the *installed* files but only on the
        # files that will be installed. Therefore we only care for sources of
        # the files in the source list.
        n_source = []

        for s in source:
            n_s = s.sources[0]
            n_s.set_tags( s.get_tags(tag_factories) )
            n_source.append( n_s )

        return ( target, n_source )


class BinaryPackager(Packager):
    """ abstract superclass for all packagers creating a binary package.

    Binary packagers are seperated from source packager by their requirement to
    create a specfile or manifest file. This file contains the contents of the
    binary packager together with some information about specific files.

    This superclass provides two needed facilities:
     * its specfile_emitter function sets up the correct list of source file
       and warns about files with no InstallBuilder attached.
    """
    def create_specfile_targets(self, kw):
        """ returns the specfile target name(s).

        This function is called by specfile_emitter to find out the specfiles
        target name.
        """
        p, v = kw['NAME'], kw['VERSION']
        return '%s-%s' % ( p, v )

    def specfile_emitter(self, target, source, env):
        """ adds the to build specfile to the source list.
        """
        # create a specfile action that is executed for building the specfile
        specfile_action = SCons.Action.Action( self.build_specfile,
                                               self.string_specfile,
                                               varlist=[ 'SPEC' ] )

        # create a specfile Builder with the right sources attached.
        specfile_builder = SCons.Builder.Builder( action = self.build_specfile,
                                                  suffix = self.specfile_suffix )

        specfile = apply( specfile_builder, [ env ], {
                          'target' : self.create_specfile_targets(env),
                          'source' : source } )

        specfile.extend( source )
        return ( target, specfile )

    def string_specfile(self, target, source, env):
        return "building specfile %s"%(target[0].abspath)

    def build_specfile(self, target, source, env):
        """ this function is called to build the specfile of name "target"
        from the source list and the settings in "env"
        """
        raise Exception( 'class does not implement build_specfile()' )

class SourcePackager(Packager):
    """ abstract superclass for all packagers which generate a source package.

    They are seperated from other packager by the their package_root attribute.
    Since before a source package is created with the help of a Tar or Zip
    builder their content needs to be moved to a package_root. For example the
    project foo with VERSION 1.2.3, will get its files placed in foo-1.2.3/.
    """
    def create_package_root(self,kw):
        """ creates the package_r oot for a given specification dict.
        """
        try:
            return kw['package_root']
        except KeyError:
            NAME, VERSION = kw['projectname'], kw['version']
            return "%s-%s"%(NAME,VERSION)

    def package_root_emitter(self, pkg_root, honor_install_location=1):
        def package_root_emitter(target, source, env):
            """ This emitter copies the sources to the src_package_root directory:
             * if a source has an install_location, not its original name is
               used but the one specified in the 'install_location' tag.
             * else its original name is used.
             * if the source file is already in the src_package_root directory, 
               nothing will be done.
            """
            new_source = []
            for s in source:
                if os.path.dirname(s.get_path()).rfind(pkg_root) != -1:
                    new_source.append(s)
                else:
                    tags     = s.get_tags()
                    new_s    = None

                    if tags.has_key( 'install_location' ) and honor_install_location:
                        my_target = strip_abs_path(tags['install_location'])
                    else:
                        my_target = strip_abs_path(s.get_path())

                    new_s = env.CopyAs( os.path.join( pkg_root, my_target ), s )[0]

                    # store the tags of our original file in the new file.
                    new_s.set_tags( s.get_tags() )
                    new_source.append( new_s )

            return (target, new_source)

        return package_root_emitter

class TagFactory:
    """An instance of this class has the responsibility to generate additional
    tags for a SCons.Node.FS.File instance.

    Subclasses have to be callable. This class definition is informally
    describing the interface.
    """

    def __call__(self, file, current_tag_dict):
        """ This call has to return additional tags in the form of a dict.
        """
        pass

    def attach_additional_info(self, info=None):
        pass

class LocationTagFactory(TagFactory):
    """ This class creates the "location" tag, which describes the install
    location of a given file.

    This is done by analyzing the builder of a given file for a InstallBuilder,
    from this builder the install location is deduced.
    """

    def __call__(self, file, current_tag_dict):
        if current_tag_dict.has_key('install_location'):
            return {}

        if file.has_builder() and\
           (file.builder.name == "InstallBuilder" or\
            file.builder.name == "InstallAsBuilder") and\
           file.has_explicit_builder():
            return { 'install_location' : file.get_path() }
        else:
            return {}


