%define name scons
%define version 0.06
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
/usr/lib/scons/SCons/Node/FS.py
/usr/lib/scons/SCons/Node/FS.pyc
/usr/lib/scons/SCons/Node/__init__.py
/usr/lib/scons/SCons/Node/__init__.pyc
/usr/lib/scons/SCons/Scanner/C.py
/usr/lib/scons/SCons/Scanner/C.pyc
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
/usr/lib/scons/SCons/Util.py
/usr/lib/scons/SCons/Util.pyc
/usr/lib/scons/SCons/__init__.py
/usr/lib/scons/SCons/__init__.pyc
/usr/lib/scons/SCons/exitfuncs.py
/usr/lib/scons/SCons/exitfuncs.pyc
%doc /usr/man/man1/scons.1.gz
