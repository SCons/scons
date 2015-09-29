=head1 Introduction

B<Cons> is a system for constructing, primarily, software, but is quite
different from previous software construction systems. Cons was designed
from the ground up to deal easily with the construction of software spread
over multiple source directories. Cons makes it easy to create build scripts
that are simple, understandable and maintainable. Cons ensures that complex
software is easily and accurately reproducible.

Cons uses a number of techniques to accomplish all of this. Construction
scripts are just Perl scripts, making them both easy to comprehend and very
flexible. Global scoping of variables is replaced with an import/export
mechanism for sharing information between scripts, significantly improving
the readability and maintainability of each script. B<Construction
environments> are introduced: these are Perl objects that capture the
information required for controlling the build process. Multiple
environments are used when different semantics are required for generating
products in the build tree. Cons implements automatic dependency analysis
and uses this to globally sequence the entire build. Variant builds are
easily produced from a single source tree. Intelligent build subsetting is
possible, when working on localized changes. Overrides can be setup to
easily override build instructions without modifying any scripts. MD5
cryptographic B<signatures> are associated with derived files, and are used
to accurately determine whether a given file needs to be rebuilt.

While offering all of the above, and more, Cons remains simple and easy to
use. This will, hopefully, become clear as you read the remainder of this
document.



=head2 Automatic global build sequencing

Because Cons does full and accurate dependency analysis, and does this
globally, for the entire build, Cons is able to use this information to take
full control of the B<sequencing> of the build. This sequencing is evident
in the above examples, and is equivalent to what you would expect for make,
given a full set of dependencies. With Cons, this extends trivially to
larger, multi-directory builds. As a result, all of the complexity involved
in making sure that a build is organized correctly--including multi-pass
hierarchical builds--is eliminated. We'll discuss this further in the next
sections.



=head1 A Model for sharing files


=head2 Some simple conventions

In any complex software system, a method for sharing build products needs to
be established. We propose a simple set of conventions which are trivial to
implement with Cons, but very effective.

The basic rule is to require that all build products which need to be shared
between directories are shared via an intermediate directory. We have
typically called this F<export>, and, in a C environment, provided
conventional sub-directories of this directory, such as F<include>, F<lib>,
F<bin>, etc.

These directories are defined by the top-level F<Construct> file. A simple
F<Construct> file for a B<Hello, World!> application, organized using
multiple directories, might look like this:

  # Construct file for Hello, World!

  # Where to put all our shared products.
  $EXPORT = '#export';

  Export qw( CONS INCLUDE LIB BIN );

  # Standard directories for sharing products.
  $INCLUDE = "$EXPORT/include";
  $LIB = "$EXPORT/lib";
  $BIN = "$EXPORT/bin";

  # A standard construction environment.
  $CONS = new cons (
	CPPPATH => $INCLUDE,	# Include path for C Compilations
	LIBPATH => $LIB,	# Library path for linking programs
	LIBS => '-lworld',	# List of standard libraries
  );

  Build qw(
	hello/Conscript
	world/Conscript
  );

The F<world> directory's F<Conscript> file looks like this:

  # Conscript file for directory world
  Import qw( CONS INCLUDE LIB );

  # Install the products of this directory
  Install $CONS $LIB, 'libworld.a';
  Install $CONS $INCLUDE, 'world.h';

  # Internal products
  Library $CONS 'libworld.a', 'world.c';

and the F<hello> directory's F<Conscript> file looks like this:

  # Conscript file for directory hello
  Import qw( CONS BIN );

  # Exported products
  Install $CONS $BIN, 'hello';

  # Internal products
  Program $CONS 'hello', 'hello.c';

To construct a B<Hello, World!> program with this directory structure, go to
the top-level directory, and invoke C<cons> with the appropriate
arguments. In the following example, we tell Cons to build the directory
F<export>. To build a directory, Cons recursively builds all known products
within that directory (only if they need rebuilding, of course). If any of
those products depend upon other products in other directories, then those
will be built, too.

  % cons export
  Install world/world.h as export/include/world.h
  cc -Iexport/include -c hello/hello.c -o hello/hello.o
  cc -Iexport/include -c world/world.c -o world/world.o
  ar r world/libworld.a world/world.o
  ar: creating world/libworld.a
  ranlib world/libworld.a
  Install world/libworld.a as export/lib/libworld.a
  cc -o hello/hello hello/hello.o -Lexport/lib -lworld
  Install hello/hello as export/bin/hello


=head2 Clean, understandable, location-independent scripts

You'll note that the two F<Conscript> files are very clean and
to-the-point. They simply specify products of the directory and how to build
those products. The build instructions are minimal: they specify which
construction environment to use, the name of the product, and the name of
the inputs. Note also that the scripts are location-independent: if you wish
to reorganize your source tree, you are free to do so: you only have to
change the F<Construct> file (in this example), to specify the new locations
of the F<Conscript> files. The use of an export tree makes this goal easy.

Note, too, how Cons takes care of little details for you. All the F<export>
directories, for example, were made automatically. And the installed files
were really hard-linked into the respective export directories, to save
space and time. This attention to detail saves considerable work, and makes
it even easier to produce simple, maintainable scripts.



=head1 Signatures

Cons uses file B<signatures> to decide if a derived file is out-of-date
and needs rebuilding.  In essence, if the contents of a file change,
or the manner in which the file is built changes, the file's signature
changes as well.  This allows Cons to decide with certainty when a file
needs rebuilding, because Cons can detect, quickly and reliably, whether
any of its dependency files have been changed.


=head2 MD5 content and build signatures

Cons uses the B<MD5> (B<Message Digest 5>) algorithm to compute file
signatures.  The MD5 algorithm computes a strong cryptographic checksum
for any given input string.  Cons can, based on configuration, use two
different MD5 signatures for a given file:

The B<content signature> of a file is an MD5 checksum of the file's
contents.  Consequently, when the contents of a file change, its content
signature changes as well.

The B<build signature> of a file is a combined MD5 checksum of:

=over 4

the signatures of all the input files used to build the file

the signatures of all dependency files discovered by source scanners
(for example, C<.h> files)

the signatures of all dependency files specified explicitly via the
C<Depends> method)

the command-line string used to build the file

=back

The build signature is, in effect, a digest of all the dependency
information for the specified file.  Consequently, a file's build
signature changes whenever any part of its dependency information
changes: a new file is added, the contents of a file on which it depends
change, there's a change to the command line used to build the file (or
any of its dependency files), etc.

For example, in the previous section, the build signature of the
F<world.o> file will include:

=over 4

the signature of the F<world.c> file

the signatures of any header files that Cons detects are included,
directly or indirectly, by F<world.c>

the text of the actual command line was used to generate F<world.o>

=back

Similarly, the build signature of the F<libworld.a> file will include
all the signatures of its constituents (and hence, transitively, the
signatures of B<their> constituents), as well as the command line that
created the file.

Note that there is no need for a derived file to depend upon any
particular F<Construct> or F<Conscript> file.  If changes to these files
affect a file, then this will be automatically reflected in its build
signature, since relevant parts of the command line are included in the
signature. Unrelated F<Construct> or F<Conscript> changes will have no
effect.


=head2 Storing signatures in .consign files

Before Cons exits, it stores the calculated signatures for all of the
files it built or examined in F<.consign> files, one per directory.
Cons uses this stored information on later invocations to decide if
derived files need to be rebuilt.

After the previous example was compiled, the F<.consign> file in the
F<build/peach/world> directory looked like this:

  world.h:985533370 - d181712f2fdc07c1f05d97b16bfad904
  world.o:985533372 2a0f71e0766927c0532977b0d2158981
  world.c:985533370 - c712f77189307907f4189b5a7ab62ff3
  libworld.a:985533374 69e568fc5241d7d25be86d581e1fb6aa

After the file name and colon, the first number is a timestamp of the
file's modification time (on UNIX systems, this is typically the number
of seconds since January 1st, 1970).  The second value is the build
signature of the file (or ``-'' in the case of files with no build
signature--that is, source files).  The third value, if any, is the
content signature of the file.


=head2 Using build signatures to decide when to rebuild files

When Cons is deciding whether to build or rebuild a derived file, it
first computes the file's current build signature.  If the file doesn't
exist, it must obviously be built.

If, however, the file already exists, Cons next compares the
modification timestamp of the file against the timestamp value in
the F<.consign> file.  If the timestamps match, Cons compares the
newly-computed build signature against the build signature in the
F<.consign> file.  If the timestamps do not match or the build
signatures do not match, the derived file is rebuilt.

After the file is built or rebuilt, Cons arranges to store the
newly-computed build signature in the F<.consign> file when it exits.


=head2 Signature example

The use of these signatures is an extremely simple, efficient, and
effective method of improving--dramatically--the reproducibility of a
system.

We'll demonstrate this with a simple example:

  # Simple "Hello, World!" Construct file
  $CFLAGS = '-g' if $ARG{DEBUG} eq 'on';
  $CONS = new cons(CFLAGS => $CFLAGS);
  Program $CONS 'hello', 'hello.c';

Notice how Cons recompiles at the appropriate times:

  % cons hello
  cc -c hello.c -o hello.o
  cc -o hello hello.o
  % cons hello
  cons: "hello" is up-to-date.
  % cons DEBUG=on hello
  cc -g -c hello.c -o hello.o
  cc -o hello hello.o
  % cons DEBUG=on hello
  cons: "hello" is up-to-date.
  % cons hello
  cc -c hello.c -o hello.o
  cc -o hello hello.o


=head2 Source-file signature configuration

Cons provides a C<SourceSignature> method that allows you to configure
how the signature should be calculated for any source file when its
signature is being used to decide if a dependent file is up-to-date.
The arguments to the C<SourceSignature> method consist of one or more
pairs of strings:

  SourceSignature 'auto/*.c' => 'content',
		  '*' => 'stored-content';

The first string in each pair is a pattern to match against derived file
path names. The pattern is a file-globbing pattern, not a Perl regular
expression; the pattern <*.l> will match all Lex source files.  The C<*>
wildcard will match across directory separators; the pattern C<foo/*.c>
would match all C source files in any subdirectory underneath the C<foo>
subdirectory.

The second string in each pair contains one of the following keywords to
specify how signatures should be calculated for source files that match
the pattern.  The available keywords are:

=over 4

=item content

Use the content signature of the source file when calculating signatures
of files that depend on it.  This guarantees correct calculation of the
file's signature for all builds, by telling Cons to read the contents of
a source file to calculate its content signature each time it is run.

=item stored-content

Use the source file's content signature as stored in the F<.consign>
file, provided the file's timestamp matches the cached timestamp value
in the F<.consign> file.  This optimizes performance, with the slight
risk of an incorrect build if a source file's contents have been changed
so quickly after its previous update that the timestamp still matches
the stored timestamp in the F<.consign> file even though the contents
have changed.

=back

The Cons default behavior of always calculating a source file's
signature from the file's contents is equivalent to specifying:

  SourceSignature '*' => 'content';

The C<*> will match all source files.  The C<content> keyword
specifies that Cons will read the contents of a source file to calculate
its signature each time it is run.

A useful global performance optimization is:

  SourceSignature '*' => 'stored-content';

This specifies that Cons will use pre-computed content signatures
from F<.consign> files, when available, rather than re-calculating a
signature from the the source file's contents each time Cons is run.  In
practice, this is safe for most build situations, and only a problem
when source files are changed automatically (by scripts, for example).
The Cons default, however, errs on the side of guaranteeing a correct
build in all situations.

Cons tries to match source file path names against the patterns in the
order they are specified in the C<SourceSignature> arguments:

  SourceSignature '/usr/repository/objects/*' => 'stored-content',
		  '/usr/repository/*' => 'content',
		  '*.y' => 'content',
		  '*' => 'stored-content';

In this example, all source files under the F</usr/repository/objects>
directory will use F<.consign> file content signatures, source files
anywhere else underneath F</usr/repository> will not use F<.consign>
signature values, all Yacc source files (C<*.y>) anywhere else will not
use F<.consign> signature values, and any other source file will use
F<.consign> signature values.


=head2 Derived-file signature configuration

Cons provides a C<SIGNATURE> construction variable that allows you to
configure how signatures are calculated for any derived file when its
signature is being used to decide if a dependent file is up-to-date.
The value of the C<SIGNATURE> construction variable is a Perl array
reference that holds one or more pairs of strings, like the arguments to
the C<SourceSignature> method.

The first string in each pair is a pattern to match against derived file
path names. The pattern is a file-globbing pattern, not a Perl regular
expression; the pattern `*.obj' will match all (Win32) object files.
The C<*> wildcard will match across directory separators; the pattern
`foo/*.a' would match all (UNIX) library archives in any subdirectory
underneath the foo subdirectory.

The second string in each pair contains one of the following keywords
to specify how signatures should be calculated for derived files that
match the pattern.  The available keywords are the same as for the
C<SourceSignature> method, with an additional keyword:

=over 4

=item build

Use the build signature of the derived file when calculating signatures
of files that depend on it.  This guarantees correct builds by forcing
Cons to rebuild any and all files that depend on the derived file.

=item content

Use the content signature of the derived file when calculating signatures
of files that depend on it.  This guarantees correct calculation of the
file's signature for all builds, by telling Cons to read the contents of
a derived file to calculate its content signature each time it is run.

=item stored-content

Use the derived file's content signature as stored in the F<.consign>
file, provided the file's timestamp matches the cached timestamp value
in the F<.consign> file.  This optimizes performance, with the slight
risk of an incorrect build if a derived file's contents have been
changed so quickly after a Cons build that the file's timestamp still
matches the stored timestamp in the F<.consign> file.

=back

The Cons default behavior (as previously described) for using
derived-file signatures is equivalent to:

  $env = new cons(SIGNATURE => ['*' => 'build']);

The C<*> will match all derived files.  The C<build> keyword specifies
that all derived files' build signatures will be used when calculating
whether a dependent file is up-to-date.

A useful alternative default C<SIGNATURE> configuration for many sites:

  $env = new cons(SIGNATURE => ['*' => 'content']);

In this configuration, derived files have their signatures calculated
from the file contents.  This adds slightly to Cons' workload, but has
the useful effect of "stopping" further rebuilds if a derived file is
rebuilt to exactly the same file contents as before, which usually
outweighs the additional computation Cons must perform.

For example, changing a comment in a C file and recompiling should
generate the exact same object file (assuming the compiler doesn't
insert a timestamp in the object file's header).  In that case,
specifying C<content> or C<stored-content> for the signature calculation
will cause Cons to recognize that the object file did not actually
change as a result of being rebuilt, and libraries or programs that
include the object file will not be rebuilt.  When C<build> is
specified, however, Cons will only "know" that the object file was
rebuilt, and proceed to rebuild any additional files that include the
object file.

Note that Cons tries to match derived file path names against the
patterns in the order they are specified in the C<SIGNATURE> array
reference:

  $env = new cons(SIGNATURE => ['foo/*.o' => 'build',
				'*.o' => 'content',
				'*.a' => 'stored-content',
				'*' => 'content']);

In this example, all object files underneath the F<foo> subdirectory
will use build signatures, all other object files (including object
files underneath other subdirectories!) will use F<.consign> file
content signatures, libraries will use F<.consign> file build
signatures, and all other derived files will use content signatures.


=head2 Debugging signature calculation

Cons provides a C<-S> option that can be used to specify what internal
Perl package Cons should use to calculate signatures.  The default Cons
behavior is equivalent to specifying C<-S md5> on the command line.

The only other package (currently) available is an C<md5::debug>
package that prints out detailed information about the MD5 signature
calculations performed by Cons:

  % cons -S md5::debug hello
  sig::md5::srcsig(hello.c)
          => |52d891204c62fe93ecb95281e1571938|
  sig::md5::collect(52d891204c62fe93ecb95281e1571938)
          => |fb0660af4002c40461a2f01fbb5ffd03|
  sig::md5::collect(52d891204c62fe93ecb95281e1571938,
                    fb0660af4002c40461a2f01fbb5ffd03,
                    cc   -c %< -o %>)
          => |f7128da6c3fe3c377dc22ade70647b39|
  sig::md5::current(||
                 eq |f7128da6c3fe3c377dc22ade70647b39|)
  cc -c hello.c -o hello.o
  sig::md5::collect()
          => |d41d8cd98f00b204e9800998ecf8427e|
  sig::md5::collect(f7128da6c3fe3c377dc22ade70647b39,
                    d41d8cd98f00b204e9800998ecf8427e,
                    cc  -o %> %<  )
          => |a0bdce7fd09e0350e7efbbdb043a00b0|
  sig::md5::current(||
                 eq |a0bdce7fd09e0350e7efbbdb043a00b0|)
  cc -o hello, hello.o







=head1 Temporary overrides

Cons provides a very simple mechanism for overriding aspects of a build. The
essence is that you write an override file containing one or more
C<Override> commands, and you specify this on the command line, when you run
C<cons>:

  % cons -o over export

will build the F<export> directory, with all derived files subject to the
overrides present in the F<over> file. If you leave out the C<-o> option,
then everything necessary to remove all overrides will be rebuilt.


=head2 Overriding environment variables

The override file can contain two types of overrides. The first is incoming
environment variables. These are normally accessible by the F<Construct>
file from the C<%ENV> hash variable. These can trivially be overridden in
the override file by setting the appropriate elements of C<%ENV> (these
could also be overridden in the user's environment, of course).


=head2 The Override command

The second type of override is accomplished with the C<Override> command,
which looks like this:

  Override <regexp>, <var1> => <value1>, <var2> => <value2>, ...;

The regular expression I<regexp> is matched against every derived file that
is a candidate for the build. If the derived file matches, then the
variable/value pairs are used to override the values in the construction
environment associated with the derived file.

Let's suppose that we have a construction environment like this:

  $CONS = new cons(
	COPT => '',
	CDBG => '-g',
	CFLAGS => '%COPT %CDBG',
  );

Then if we have an override file F<over> containing this command:

  Override '\.o$', COPT => '-O', CDBG => '';

then any C<cons> invocation with C<-o over> that creates F<.o> files via
this environment will cause them to be compiled with C<-O >and no C<-g>. The
override could, of course, be restricted to a single directory by the
appropriate selection of a regular expression.

Here's the original version of the Hello, World! program, built with this
environment. Note that Cons rebuilds the appropriate pieces when the
override is applied or removed:

  % cons hello
  cc -g -c hello.c -o hello.o
  cc -o hello hello.o
  % cons -o over hello
  cc -O -c hello.c -o hello.o
  cc -o hello hello.o
  % cons -o over hello
  cons: "hello" is up-to-date.
  % cons hello
  cc -g -c hello.c -o hello.o
  cc -o hello hello.o

It's important that the C<Override> command only be used for temporary,
on-the-fly overrides necessary for development because the overrides are not
platform independent and because they rely too much on intimate knowledge of
the workings of the scripts. For temporary use, however, they are exactly
what you want.

Note that it is still useful to provide, say, the ability to create a fully
optimized version of a system for production use--from the F<Construct> and
F<Conscript> files. This way you can tailor the optimized system to the
platform. Where optimizer trade-offs need to be made (particular files may
not be compiled with full optimization, for example), then these can be
recorded for posterity (and reproducibility) directly in the scripts.



=head2 The C<Module> method

The C<Module> method is a combination of the C<Program> and C<Command>
methods. Rather than generating an executable program directly, this command
allows you to specify your own command to actually generate a module. The
method is invoked as follows:

  Module $env <module name>, <source or object files>, <construction command>;

This command is useful in instances where you wish to create, for example,
dynamically loaded modules, or statically linked code libraries.




=head2 The C<RuleSet> method

The C<RuleSet> method returns the construction variables for building
various components with one of the rule sets supported by Cons.  The
currently supported rule sets are:

=over 4

=item msvc

Rules for the Microsoft Visual C++ compiler suite.

=item unix

Generic rules for most UNIX-like compiler suites.

=back

On systems with more than one available compiler suite, this allows you
to easily create side-by-side environments for building software with
multiple tools:

    $msvcenv = new cons(RuleSet("msvc"));
    $cygnusenv = new cons(RuleSet("unix"));

In the future, this could also be extended to other platforms that
have different default rule sets.


=head2 The C<DefaultRules> method

The C<DefaultRules> method sets the default construction variables that
will be returned by the C<new> method to the specified arguments:

  DefaultRules(CC     => 'gcc',
	       CFLAGS => '',
	       CCCOM  => '%CC %CFLAGS %_IFLAGS -c %< -o %>');
  $env = new cons();
  # $env now contains *only* the CC, CFLAGS,
  # and CCCOM construction variables

Combined with the C<RuleSet> method, this also provides an easy way
to set explicitly the default build environment to use some supported
toolset other than the Cons defaults:

    # use a UNIX-like tool suite (like cygwin) on Win32
    DefaultRules(RuleSet('unix'));
    $env = new cons();

Note that the C<DefaultRules> method completely replaces the default
construction environment with the specified arguments, it does not
simply override the existing defaults.  To override one or more
variables in a supported C<RuleSet>, append the variables and values:

  DefaultRules(RuleSet('unix'), CFLAGS => '-O3');
  $env1 = new cons();
  $env2 = new cons();
  # both $env1 and $env2 have 'unix' defaults
  # with CFLAGS set to '-O3'








=head2 The C<SourcePath> method

The C<SourcePath> mathod returns the real source path name of a file,
as opposed to the path name within a build directory.  It is invoked
as follows:

  $path = SourcePath <buildpath>;


=head2 The C<ConsPath> method

The C<ConsPath> method returns true if the supplied path is a derivable
file, and returns undef (false) otherwise.
It is invoked as follows:

  $result = ConsPath <path>;


=head2 The C<SplitPath> method

The C<SplitPath> method looks up multiple path names in a string separated
by the default path separator for the operating system (':' on UNIX
systems, ';' on Windows NT), and returns the fully-qualified names.
It is invoked as follows:

  @paths = SplitPath <pathlist>;

The C<SplitPath> method will convert  names prefixed '#' to the
appropriate top-level build name (without the '#') and will convert
relative names to top-level names.


=head2 The C<DirPath> method

The C<DirPath> method returns the build path name(s) of a directory or
list of directories.  It is invoked as follows:

  $cwd = DirPath <paths>;

The most common use for the C<DirPath> method is:

  $cwd = DirPath '.';

to fetch the path to the current directory of a subsidiary F<Conscript>
file.


=head2 The C<FilePath> method

The C<FilePath> method returns the build path name(s) of a file or
list of files.  It is invoked as follows:

  $file = FilePath <path>;
