%define name scons
%define version 0.10
%define release 1

Summary: an Open Source software construction tool
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
#Copyright: Steven Knight
License: MIT, freely distributable
Group: Development/Tools
BuildRoot: %{_tmppath}/%{name}-buildroot
Prefix: %{_prefix}
BuildArchitectures: noarch
Vendor: Steven Knight <knight@scons.org>
Packager: Steven Knight <knight@scons.org>
Requires: python >= 1.5
Url: http://www.scons.org/

%description
SCons is an Open Source software construction tool--that is, a build
tool; an improved substitute for the classic Make utility; a better way
to build software.  SCons is based on the design which won the Software
Carpentry build tool design competition in August 2000.

SCons "configuration files" are Python scripts, eliminating the need
to learn a new build tool syntax.  SCons maintains a global view of
all dependencies in a tree, and can scan source (or other) files for
implicit dependencies, such as files specified on #include lines.  SCons
uses MD5 signatures to rebuild only when the contents of a file have
really changed, not just when the timestamp has been touched.  SCons
supports side-by-side variant builds, and is easily extended with user-
defined Builder and/or Scanner objects.

%prep
%setup

%build
python setup.py build

%install
python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
mkdir -p $RPM_BUILD_ROOT/usr/man/man1
gzip -c scons.1 > $RPM_BUILD_ROOT/usr/man/man1/scons.1.gz

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/usr/bin/scons
/usr/lib/scons/SCons/Action.py
/usr/lib/scons/SCons/Action.pyc
/usr/lib/scons/SCons/Builder.py
/usr/lib/scons/SCons/Builder.pyc
/usr/lib/scons/SCons/Defaults.py
/usr/lib/scons/SCons/Defaults.pyc
/usr/lib/scons/SCons/Environment.py
/usr/lib/scons/SCons/Environment.pyc
/usr/lib/scons/SCons/Errors.py
/usr/lib/scons/SCons/Errors.pyc
/usr/lib/scons/SCons/Job.py
/usr/lib/scons/SCons/Job.pyc
/usr/lib/scons/SCons/Node/Alias.py
/usr/lib/scons/SCons/Node/Alias.pyc
/usr/lib/scons/SCons/Node/FS.py
/usr/lib/scons/SCons/Node/FS.pyc
/usr/lib/scons/SCons/Node/__init__.py
/usr/lib/scons/SCons/Node/__init__.pyc
/usr/lib/scons/SCons/Optik/__init__.py
/usr/lib/scons/SCons/Optik/__init__.pyc
/usr/lib/scons/SCons/Optik/errors.py
/usr/lib/scons/SCons/Optik/errors.pyc
/usr/lib/scons/SCons/Optik/option.py
/usr/lib/scons/SCons/Optik/option.pyc
/usr/lib/scons/SCons/Optik/option_parser.py
/usr/lib/scons/SCons/Optik/option_parser.pyc
/usr/lib/scons/SCons/Options.py
/usr/lib/scons/SCons/Options.pyc
/usr/lib/scons/SCons/Platform/cygwin.py
/usr/lib/scons/SCons/Platform/cygwin.pyc
/usr/lib/scons/SCons/Platform/os2.py
/usr/lib/scons/SCons/Platform/os2.pyc
/usr/lib/scons/SCons/Platform/posix.py
/usr/lib/scons/SCons/Platform/posix.pyc
/usr/lib/scons/SCons/Platform/win32.py
/usr/lib/scons/SCons/Platform/win32.pyc
/usr/lib/scons/SCons/Platform/__init__.py
/usr/lib/scons/SCons/Platform/__init__.pyc
/usr/lib/scons/SCons/Scanner/C.py
/usr/lib/scons/SCons/Scanner/C.pyc
/usr/lib/scons/SCons/Scanner/Fortran.py
/usr/lib/scons/SCons/Scanner/Fortran.pyc
/usr/lib/scons/SCons/Scanner/Prog.py
/usr/lib/scons/SCons/Scanner/Prog.pyc
/usr/lib/scons/SCons/Scanner/__init__.py
/usr/lib/scons/SCons/Scanner/__init__.pyc
/usr/lib/scons/SCons/Script/__init__.py
/usr/lib/scons/SCons/Script/__init__.pyc
/usr/lib/scons/SCons/Script/SConscript.py
/usr/lib/scons/SCons/Script/SConscript.pyc
/usr/lib/scons/SCons/Sig/MD5.py
/usr/lib/scons/SCons/Sig/MD5.pyc
/usr/lib/scons/SCons/Sig/TimeStamp.py
/usr/lib/scons/SCons/Sig/TimeStamp.pyc
/usr/lib/scons/SCons/Sig/__init__.py
/usr/lib/scons/SCons/Sig/__init__.pyc
/usr/lib/scons/SCons/Taskmaster.py
/usr/lib/scons/SCons/Taskmaster.pyc
/usr/lib/scons/SCons/Tool/__init__.py
/usr/lib/scons/SCons/Tool/__init__.pyc
/usr/lib/scons/SCons/Tool/ar.py
/usr/lib/scons/SCons/Tool/ar.pyc
/usr/lib/scons/SCons/Tool/default.py
/usr/lib/scons/SCons/Tool/default.pyc
/usr/lib/scons/SCons/Tool/dvipdf.py
/usr/lib/scons/SCons/Tool/dvipdf.pyc
/usr/lib/scons/SCons/Tool/dvips.py
/usr/lib/scons/SCons/Tool/dvips.pyc
/usr/lib/scons/SCons/Tool/g++.py
/usr/lib/scons/SCons/Tool/g++.pyc
/usr/lib/scons/SCons/Tool/g77.py
/usr/lib/scons/SCons/Tool/g77.pyc
/usr/lib/scons/SCons/Tool/gas.py
/usr/lib/scons/SCons/Tool/gas.pyc
/usr/lib/scons/SCons/Tool/gcc.py
/usr/lib/scons/SCons/Tool/gcc.pyc
/usr/lib/scons/SCons/Tool/gnulink.py
/usr/lib/scons/SCons/Tool/gnulink.pyc
/usr/lib/scons/SCons/Tool/icc.py
/usr/lib/scons/SCons/Tool/icc.pyc
/usr/lib/scons/SCons/Tool/ifl.py
/usr/lib/scons/SCons/Tool/ifl.pyc
/usr/lib/scons/SCons/Tool/ilink.py
/usr/lib/scons/SCons/Tool/ilink.pyc
/usr/lib/scons/SCons/Tool/latex.py
/usr/lib/scons/SCons/Tool/latex.pyc
/usr/lib/scons/SCons/Tool/lex.py
/usr/lib/scons/SCons/Tool/lex.pyc
/usr/lib/scons/SCons/Tool/masm.py
/usr/lib/scons/SCons/Tool/masm.pyc
/usr/lib/scons/SCons/Tool/mingw.py
/usr/lib/scons/SCons/Tool/mingw.pyc
/usr/lib/scons/SCons/Tool/mslib.py
/usr/lib/scons/SCons/Tool/mslib.pyc
/usr/lib/scons/SCons/Tool/mslink.py
/usr/lib/scons/SCons/Tool/mslink.pyc
/usr/lib/scons/SCons/Tool/msvc.py
/usr/lib/scons/SCons/Tool/msvc.pyc
/usr/lib/scons/SCons/Tool/nasm.py
/usr/lib/scons/SCons/Tool/nasm.pyc
/usr/lib/scons/SCons/Tool/pdflatex.py
/usr/lib/scons/SCons/Tool/pdflatex.pyc
/usr/lib/scons/SCons/Tool/pdftex.py
/usr/lib/scons/SCons/Tool/pdftex.pyc
/usr/lib/scons/SCons/Tool/tar.py
/usr/lib/scons/SCons/Tool/tar.pyc
/usr/lib/scons/SCons/Tool/tex.py
/usr/lib/scons/SCons/Tool/tex.pyc
/usr/lib/scons/SCons/Tool/yacc.py
/usr/lib/scons/SCons/Tool/yacc.pyc
/usr/lib/scons/SCons/Util.py
/usr/lib/scons/SCons/Util.pyc
/usr/lib/scons/SCons/Warnings.py
/usr/lib/scons/SCons/Warnings.pyc
/usr/lib/scons/SCons/__init__.py
/usr/lib/scons/SCons/__init__.pyc
/usr/lib/scons/SCons/exitfuncs.py
/usr/lib/scons/SCons/exitfuncs.pyc
%doc /usr/man/man1/scons.1.gz
