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
import string
import sys
import TestCmd
import unittest

from SCons.Tool.msvs import *
import SCons.Util
import SCons.Warnings

regdata_6a = string.split(r'''[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio]
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\6.0]
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\6.0\ServicePacks]
"sp3"=""
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\6.0\Setup]
"VsCommonDir"="C:\Program Files\Microsoft Visual Studio\Common"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\6.0\Setup\Microsoft Developer Network Library - Visual Studio 6.0a]
"ProductDir"="C:\Program Files\Microsoft Visual Studio\MSDN98\98VSa\1033"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\6.0\Setup\Microsoft Visual C++]
"ProductDir"="C:\Program Files\Microsoft Visual Studio\VC98"
''','\n')

regdata_6b = string.split(r'''[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio]
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\6.0]
"InstallDir"="C:\VS6\Common\IDE\IDE98"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\6.0\ServicePacks]
"sp5"=""
"latest"=dword:00000005
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\6.0\Setup]
"VsCommonDir"="C:\VS6\Common"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\6.0\Setup\Microsoft Visual Basic]
"ProductDir"="C:\VS6\VB98"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\6.0\Setup\Microsoft Visual C++]
"ProductDir"="C:\VS6\VC98"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\6.0\Setup\Microsoft Visual Studio]
"ProductDir"="C:\VS6"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\6.0\Setup\Microsoft VSEE Client]
"ProductDir"="C:\VS6\Common\Tools"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\6.0\Setup\Visual Studio 98]
''','\n')

regdata_7 = string.split(r'''
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.0]
"InstallDir"="C:\Program Files\Microsoft Visual Studio .NET\Common7\IDE\"
"Source Directories"="C:\Program Files\Microsoft Visual Studio .NET\Vc7\crt\;C:\Program Files\Microsoft Visual Studio .NET\Vc7\atlmfc\src\mfc\;C:\Program Files\Microsoft Visual Studio .NET\Vc7\atlmfc\src\atl\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.0\InstalledProducts]
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.0\InstalledProducts\CrystalReports]
@="#15007"
"Package"="{F05E92C6-8346-11D3-B4AD-00A0C9B04E7B}"
"ProductDetails"="#15009"
"LogoID"="0"
"PID"="#15008"
"UseInterface"=dword:00000001
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.0\InstalledProducts\Visual Basic.NET]
@=""
"DefaultProductAttribute"="VB"
"Package"="{164B10B9-B200-11D0-8C61-00A0C91E29D5}"
"UseInterface"=dword:00000001
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.0\InstalledProducts\Visual C#]
@=""
"Package"="{FAE04EC1-301F-11d3-BF4B-00C04F79EFBC}"
"UseInterface"=dword:00000001
"DefaultProductAttribute"="C#"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.0\InstalledProducts\VisualC++]
"UseInterface"=dword:00000001
"Package"="{F1C25864-3097-11D2-A5C5-00C04F7968B4}"
"DefaultProductAttribute"="VC"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.0\Setup]
"Dbghelp_path"="C:\Program Files\Microsoft Visual Studio .NET\Common7\IDE\"
"dw_dir"="C:\Program Files\Microsoft Visual Studio .NET\Common7\IDE\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.0\Setup\MSDN]
"ProductDir"="C:\Program Files\Microsoft Visual Studio .NET\Msdn\1033\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.0\Setup\Servicing\SKU]
"Visual Studio .NET Professional - English"="{D0610409-7D65-11D5-A54F-0090278A1BB8}"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.0\Setup\VB]
"ProductDir"="C:\Program Files\Microsoft Visual Studio .NET\Vb7\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.0\Setup\VC]
"ProductDir"="C:\Program Files\Microsoft Visual Studio .NET\Vc7\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.0\Setup\VC#]
"ProductDir"="C:\Program Files\Microsoft Visual Studio .NET\VC#\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.0\Setup\Visual Studio .NET Professional - English]
"InstallSuccess"=dword:00000001
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.0\Setup\VS]
"EnvironmentDirectory"="C:\Program Files\Microsoft Visual Studio .NET\Common7\IDE\"
"EnvironmentPath"="C:\Program Files\Microsoft Visual Studio .NET\Common7\IDE\devenv.exe"
"VS7EnvironmentLocation"="C:\Program Files\Microsoft Visual Studio .NET\Common7\IDE\devenv.exe"
"MSMDir"="C:\Program Files\Common Files\Merge Modules\"
"ProductDir"="C:\Program Files\Microsoft Visual Studio .NET\"
"VS7CommonBinDir"="C:\Program Files\Microsoft Visual Studio .NET\Common7\Tools\"
"VS7CommonDir"="C:\Program Files\Microsoft Visual Studio .NET\Common7\"
"VSUpdateDir"="C:\Program Files\Microsoft Visual Studio .NET\Setup\VSUpdate\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.0\Setup\VS\BuildNumber]
"1033"="7.0.9466"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.0\Setup\VS\Pro]
"ProductDir"="C:\Program Files\Microsoft Visual Studio .NET\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.0\VC]
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.0\VC\VC_OBJECTS_PLATFORM_INFO]
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.0\VC\VC_OBJECTS_PLATFORM_INFO\Win32]
@="{A54AAE91-30C2-11D3-87BF-A04A4CC10000}"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.0\VC\VC_OBJECTS_PLATFORM_INFO\Win32\Directories]
"Path Dirs"="$(VCInstallDir)bin;$(VSInstallDir)Common7\Tools\bin\prerelease;$(VSInstallDir)Common7\Tools\bin;$(VSInstallDir)Common7\tools;$(VSInstallDir)Common7\ide;C:\Program Files\HTML Help Workshop\;$(FrameworkSDKDir)bin;$(FrameworkDir)$(FrameworkVersion);C:\perl\bin;C:\cygwin\bin;c:\cygwin\usr\bin;C:\bin;C:\program files\perforce;C:\cygwin\usr\local\bin\i686-pc-cygwin;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem"
"Library Dirs"="$(VCInstallDir)lib;$(VCInstallDir)atlmfc\lib;$(VCInstallDir)PlatformSDK\lib\prerelease;$(VCInstallDir)PlatformSDK\lib;$(FrameworkSDKDir)lib"
"Include Dirs"="$(VCInstallDir)include;$(VCInstallDir)atlmfc\include;$(VCInstallDir)PlatformSDK\include\prerelease;$(VCInstallDir)PlatformSDK\include;$(FrameworkSDKDir)include"
"Source Dirs"="$(VCInstallDir)atlmfc\src\mfc;$(VCInstallDir)atlmfc\src\atl;$(VCInstallDir)crt\src"
"Reference Dirs"=""
''','\n')

regdata_7_1 = string.split(r'''
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1]
@=""
"Source Directories"="C:\Program Files\Microsoft Visual Studio .NET 2003\Vc7\crt\src\;C:\Program Files\Microsoft Visual Studio .NET 2003\Vc7\atlmfc\src\mfc\;C:\Program Files\Microsoft Visual Studio .NET 2003\Vc7\atlmfc\src\atl\"
"ThisVersionSolutionCLSID"="{246C57AE-40DD-4d6b-9E8D-B0F5757BB2A8}"
"ThisVersionDTECLSID"="{8CD2DD97-4EC1-4bc4-9359-89A3EEDD57A6}"
"InstallDir"="C:\Program Files\Microsoft Visual Studio .NET 2003\Common7\IDE\"
"CLR Version"="v1.1.4322"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\InstalledProducts]
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\InstalledProducts\Smart Device Extensions]
"UseInterface"=dword:00000001
"VS7InstallDir"="C:\Program Files\Microsoft Visual Studio .NET 2003\"
"VBDeviceInstallDir"="C:\Program Files\Microsoft Visual Studio .NET 2003\VB7\"
"CSharpDeviceInstallDir"="C:\Program Files\Microsoft Visual Studio .NET 2003\VC#\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\InstalledProducts\Visual Basic.NET]
"UseInterface"=dword:00000001
"Package"="{164B10B9-B200-11D0-8C61-00A0C91E29D5}"
"DefaultProductAttribute"="VB"
@=""
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\InstalledProducts\Visual C#]
"DefaultProductAttribute"="C#"
"UseInterface"=dword:00000001
"Package"="{FAE04EC1-301F-11D3-BF4B-00C04F79EFBC}"
@=""
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\InstalledProducts\Visual JSharp]
@=""
"Package"="{E6FDF8B0-F3D1-11D4-8576-0002A516ECE8}"
"UseInterface"=dword:00000001
"DefaultProductAttribute"="Visual JSharp"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\InstalledProducts\VisualC++]
"UseInterface"=dword:00000001
"Package"="{F1C25864-3097-11D2-A5C5-00C04F7968B4}"
"DefaultProductAttribute"="VC"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\Setup]
"Dbghelp_path"="C:\Program Files\Microsoft Visual Studio .NET 2003\Common7\IDE\"
"dw_dir"="C:\Program Files\Microsoft Visual Studio .NET 2003\Common7\IDE\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\Setup\CSDPROJ]
"ProductDir"="C:\Program Files\Microsoft Visual Studio .NET 2003\VC#\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\Setup\JSHPROJ]
"ProductDir"="C:\Program Files\Microsoft Visual Studio .NET 2003\VJ#\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\Setup\Servicing]
"CurrentSULevel"=dword:00000000
"CurrentSPLevel"=dword:00000000
"Server Path"=""
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\Setup\Servicing\Package]
"FxSDK"=""
"VB"=""
"VC"=""
"VCS"=""
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\Setup\Servicing\SKU]
"Visual Studio .NET Professional 2003 - English"="{20610409-CA18-41A6-9E21-A93AE82EE7C5}"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\Setup\VB]
"ProductDir"="C:\Program Files\Microsoft Visual Studio .NET 2003\Vb7\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\Setup\VBDPROJ]
"ProductDir"="C:\Program Files\Microsoft Visual Studio .NET 2003\Vb7\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\Setup\VC]
"ProductDir"="C:\Program Files\Microsoft Visual Studio .NET 2003\Vc7\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\Setup\VC#]
"ProductDir"="C:\Program Files\Microsoft Visual Studio .NET 2003\VC#\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\Setup\Visual Studio .NET Professional 2003 - English]
"InstallSuccess"=dword:00000001
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\Setup\VS]
"EnvironmentDirectory"="C:\Program Files\Microsoft Visual Studio .NET 2003\Common7\IDE\"
"EnvironmentPath"="C:\Program Files\Microsoft Visual Studio .NET 2003\Common7\IDE\devenv.exe"
"VS7EnvironmentLocation"="C:\Program Files\Microsoft Visual Studio .NET 2003\Common7\IDE\devenv.exe"
"MSMDir"="C:\Program Files\Common Files\Merge Modules\"
"VS7CommonBinDir"="C:\Program Files\Microsoft Visual Studio .NET 2003\Common7\Tools\"
"VS7CommonDir"="C:\Program Files\Microsoft Visual Studio .NET 2003\Common7\"
"ProductDir"="C:\Program Files\Microsoft Visual Studio .NET 2003\"
"VSUpdateDir"="C:\Program Files\Microsoft Visual Studio .NET 2003\Setup\VSUpdate\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\Setup\VS\BuildNumber]
"1033"="7.1.3088"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\Setup\VS\Pro]
"ProductDir"="C:\Program Files\Microsoft Visual Studio .NET 2003\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\VC]
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\VC\VC_OBJECTS_PLATFORM_INFO]
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\VC\VC_OBJECTS_PLATFORM_INFO\Win32]
@="{759354D0-6B42-4705-AFFB-56E34D2BC3D4}"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\VC\VC_OBJECTS_PLATFORM_INFO\Win32\Directories]
"Path Dirs"="$(VCInstallDir)bin;$(VSInstallDir)Common7\Tools\bin\prerelease;$(VSInstallDir)Common7\Tools\bin;$(VSInstallDir)Common7\tools;$(VSInstallDir)Common7\ide;C:\Program Files\HTML Help Workshop\;$(FrameworkSDKDir)bin;$(FrameworkDir)$(FrameworkVersion);C:\Perl\bin\;c:\bin;c:\cygwin\bin;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\Program Files\Common Files\Avid;C:\Program Files\backburner 2\;C:\Program Files\cvsnt;C:\Program Files\Subversion\bin;C:\Program Files\Common Files\Adobe\AGL;C:\Program Files\HTMLDoc"
"Library Dirs"="$(VCInstallDir)lib;$(VCInstallDir)atlmfc\lib;$(VCInstallDir)PlatformSDK\lib\prerelease;$(VCInstallDir)PlatformSDK\lib;$(FrameworkSDKDir)lib"
"Include Dirs"="$(VCInstallDir)include;$(VCInstallDir)atlmfc\include;$(VCInstallDir)PlatformSDK\include\prerelease;$(VCInstallDir)PlatformSDK\include;$(FrameworkSDKDir)include"
"Source Dirs"="$(VCInstallDir)atlmfc\src\mfc;$(VCInstallDir)atlmfc\src\atl;$(VCInstallDir)crt\src"
"Reference Dirs"="$(FrameWorkDir)$(FrameWorkVersion)"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\7.1\VC\VC_OBJECTS_PLATFORM_INFO\Win32\ToolDefaultExtensionLists]
"VCCLCompilerTool"="*.cpp;*.cxx;*.cc;*.c"
"VCLinkerTool"="*.obj;*.res;*.lib;*.rsc"
"VCLibrarianTool"="*.obj;*.res;*.lib;*.rsc"
"VCMIDLTool"="*.idl;*.odl"
"VCCustomBuildTool"="*.bat"
"VCResourceCompilerTool"="*.rc"
"VCPreBuildEventTool"="*.bat"
"VCPreLinkEventTool"="*.bat"
"VCPostBuildEventTool"="*.bat"
"VCBscMakeTool"="*.sbr"
"VCNMakeTool"=""
"VCWebServiceProxyGeneratorTool"="*.discomap"
"VCWebDeploymentTool"=""
"VCALinkTool"="*.resources"
"VCManagedResourceCompilerTool"="*.resx"
"VCXMLDataGeneratorTool"="*.xsd"
"VCManagedWrapperGeneratorTool"=""
"VCAuxiliaryManagedWrapperGeneratorTool"=""
"VCPrimaryInteropTool"=""
''','\n')

regdata_8exp = string.split(r'''
[HKEY_LOCAL_MACHINE\Software\Microsoft\VCExpress\8.0]
"CLR Version"="v2.0.50727"
"ApplicationID"="VCExpress"
"SecurityAppID"="{741726F6-1EAE-4680-86A6-6085E8872CF8}"
"InstallDir"="C:\Program Files\Microsoft Visual Studio 8\Common7\IDE\"
"EnablePreloadCLR"=dword:00000001
"RestoreAppPath"=dword:00000001
[HKEY_LOCAL_MACHINE\Software\Microsoft\VCExpress\8.0\InstalledProducts]
[HKEY_LOCAL_MACHINE\Software\Microsoft\VCExpress\8.0\InstalledProducts\Microsoft Visual C++]
"UseInterface"=dword:00000001
"Package"="{F1C25864-3097-11D2-A5C5-00C04F7968B4}"
"DefaultProductAttribute"="VC"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VCExpress\8.0\Setup]
[HKEY_LOCAL_MACHINE\Software\Microsoft\VCExpress\8.0\Setup\VC]
"ProductDir"="C:\Program Files\Microsoft Visual Studio 8\VC\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VCExpress\8.0\Setup\VS]
"ProductDir"="C:\Program Files\Microsoft Visual Studio 8\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VCExpress\8.0\VC]
[HKEY_LOCAL_MACHINE\Software\Microsoft\VCExpress\8.0\VC\VC_OBJECTS_PLATFORM_INFO]
[HKEY_LOCAL_MACHINE\Software\Microsoft\VCExpress\8.0\VC\VC_OBJECTS_PLATFORM_INFO\Win32]
@="{72f11281-2429-11d7-8bf6-00b0d03daa06}"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VCExpress\8.0\VC\VC_OBJECTS_PLATFORM_INFO\Win32\ToolDefaultExtensionLists]
"VCCLCompilerTool"="*.cpp;*.cxx;*.cc;*.c"
"VCLinkerTool"="*.obj;*.res;*.lib;*.rsc;*.licenses"
"VCLibrarianTool"="*.obj;*.res;*.lib;*.rsc"
"VCMIDLTool"="*.idl;*.odl"
"VCCustomBuildTool"="*.bat"
"VCResourceCompilerTool"="*.rc"
"VCPreBuildEventTool"="*.bat"
"VCPreLinkEventTool"="*.bat"
"VCPostBuildEventTool"="*.bat"
"VCBscMakeTool"="*.sbr"
"VCFxCopTool"="*.dll;*.exe"
"VCNMakeTool"=""
"VCWebServiceProxyGeneratorTool"="*.discomap"
"VCWebDeploymentTool"=""
"VCALinkTool"="*.resources"
"VCManagedResourceCompilerTool"="*.resx"
"VCXMLDataGeneratorTool"="*.xsd"
"VCManifestTool"="*.manifest"
"VCXDCMakeTool"="*.xdc"
''','\n')

regdata_cv = string.split(r'''[HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion]
"ProgramFilesDir"="C:\Program Files"
"CommonFilesDir"="C:\Program Files\Common Files"
"MediaPath"="C:\WINDOWS\Media"
''','\n')

regdata_none = []

class DummyEnv:
    def __init__(self, dict=None):
        if dict:
            self.dict = dict
        else:
            self.dict = {}

    def Dictionary(self, key = None):
        if not key:
            return self.dict
        return self.dict[key]

    def __setitem__(self,key,value):
        self.dict[key] = value

    def __getitem__(self,key):
        return self.dict[key]

    def has_key(self,name):
        return self.dict.has_key(name)

class RegKey:
    """key class for storing an 'open' registry key"""
    def __init__(self,key):
        self.key = key

class RegNode:
    """node in the dummy registry"""
    def __init__(self,name):
        self.valdict = {}
        self.keydict = {}
        self.keyarray = []
        self.valarray = []
        self.name = name

    def value(self,val):
        if self.valdict.has_key(val):
            return (self.valdict[val],1)
        else:
            raise SCons.Util.RegError

    def addValue(self,name,val):
        self.valdict[name] = val
        self.valarray.append(name)

    def valindex(self,index):
        rv = None
        try:
            rv = (self.valarray[index],self.valdict[self.valarray[index]],1)
        except KeyError:
            raise SCons.Util.RegError
        return rv

    def key(self,key,sep = '\\'):
        if key.find(sep) != -1:
            keyname, subkeys = key.split(sep,1)
        else:
            keyname = key
            subkeys = ""
        try:
            # recurse, and return the lowest level key node
            if subkeys:
                return self.keydict[keyname].key(subkeys)
            else:
                return self.keydict[keyname]
        except KeyError:
            raise SCons.Util.RegError

    def addKey(self,name,sep = '\\'):
        if string.find(name, sep) != -1:
            keyname, subkeys = string.split(name, sep, 1)
        else:
            keyname = name
            subkeys = ""

        if not self.keydict.has_key(keyname):
            self.keydict[keyname] = RegNode(keyname)
            self.keyarray.append(keyname)

        # recurse, and return the lowest level key node
        if subkeys:
            return self.keydict[keyname].addKey(subkeys)
        else:
            return self.keydict[keyname]

    def keyindex(self,index):
        return self.keydict[self.keyarray[index]]

    def __str__(self):
        return self._doStr()

    def _doStr(self, indent = ''):
        rv = ""
        for value in self.valarray:
            rv = rv + '%s"%s" = "%s"\n' % (indent, value, self.valdict[value])
        for key in self.keyarray:
            rv = rv + "%s%s: {\n"%(indent, key)
            rv = rv + self.keydict[key]._doStr(indent + '  ')
            rv = rv + indent + '}\n'
        return rv

class DummyRegistry:
    """registry class for storing fake registry attributes"""
    def __init__(self,data):
        """parse input data into the fake registry"""
        self.root = RegNode('REGISTRY')
        self.root.addKey('HKEY_LOCAL_MACHINE')
        self.root.addKey('HKEY_CURRENT_USER')
        self.root.addKey('HKEY_USERS')
        self.root.addKey('HKEY_CLASSES_ROOT')

        self.parse(data)

    def parse(self, data):
        parent = self.root
        keymatch = re.compile('^\[(.*)\]$')
        valmatch = re.compile('^(?:"(.*)"|[@])="(.*)"$')
        for line in data:
            m1 = keymatch.match(line)
            if m1:
                # add a key, set it to current parent
                parent = self.root.addKey(m1.group(1))
            else:
                m2 = valmatch.match(line)
                if m2:
                    parent.addValue(m2.group(1),m2.group(2))

    def OpenKeyEx(self,root,key):
        if root == SCons.Util.HKEY_CLASSES_ROOT:
            mykey = 'HKEY_CLASSES_ROOT\\' + key
        if root == SCons.Util.HKEY_USERS:
            mykey = 'HKEY_USERS\\' + key
        if root == SCons.Util.HKEY_CURRENT_USER:
            mykey = 'HKEY_CURRENT_USER\\' + key
        if root == SCons.Util.HKEY_LOCAL_MACHINE:
            mykey = 'HKEY_LOCAL_MACHINE\\' + key
        #print "Open Key",mykey
        return self.root.key(mykey)

def DummyOpenKeyEx(root, key):
    return registry.OpenKeyEx(root,key)

def DummyEnumKey(key, index):
    rv = None
    try:
        rv = key.keyarray[index]
    except IndexError:
        raise SCons.Util.RegError
#    print "Enum Key",key.name,"[",index,"] =>",rv
    return rv

def DummyEnumValue(key, index):
    rv = key.valindex(index)
#    print "Enum Value",key.name,"[",index,"] =>",rv
    return rv

def DummyQueryValue(key, value):
    rv = key.value(value)
#    print "Query Value",key.name+"\\"+value,"=>",rv
    return rv

def DummyExists(path):
    return 1

class msvsTestCase(unittest.TestCase):
    def setUp(self):
        global registry
        registry = self.registry

    def test_get_default_visual_studio_version(self):
        """Test retrieval of the default visual studio version"""
        env = DummyEnv()
        v1 = get_default_visualstudio_version(env)
        assert env['MSVS_VERSION'] == self.default_version, env['MSVS_VERSION']
        assert env['MSVS']['VERSION'] == self.default_version, env['MSVS']['VERSION']
        assert v1 == self.default_version, v1

        env = DummyEnv({'MSVS_VERSION':'7.0'})
        v2 = get_default_visualstudio_version(env)
        assert env['MSVS_VERSION'] == '7.0', env['MSVS_VERSION']
        assert env['MSVS']['VERSION'] == '7.0', env['MSVS']['VERSION']
        assert v2 == '7.0', v2

        env = DummyEnv()
        v3 = get_default_visualstudio_version(env)
        if v3 == '7.1':
            override = '7.0'
        else:
            override = '7.1'
        env['MSVS_VERSION'] = override
        v3 = get_default_visualstudio_version(env)
        assert env['MSVS_VERSION'] == override, env['MSVS_VERSION']
        assert env['MSVS']['VERSION'] == override, env['MSVS']['VERSION']
        assert v3 == override, v3

    def test_get_visual_studio_versions(self):
        """Test retrieval of the list of visual studio versions"""
        v1 = get_visualstudio_versions()
        assert not v1 or v1[0] == self.highest_version, v1
        assert len(v1) == self.number_of_versions, v1

    def test_get_msvs_install_dirs(self):
        """Test retrieval of the list of visual studio installed locations"""
        v1 = get_msvs_install_dirs()
        assert v1 == self.default_install_loc, v1
        for key, loc in self.install_locs.items():
            v2 = get_msvs_install_dirs(key)
            assert v2 == loc, key + ': ' + str(v2)

class msvs6aTestCase(msvsTestCase):
    """Test MSVS 6 Registry"""
    registry = DummyRegistry(regdata_6a + regdata_cv)
    default_version = '6.0'
    highest_version = '6.0'
    number_of_versions = 1
    install_locs = {
        '6.0' : {'VSINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio', 'VCINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio\\VC98'},
        '7.0' : {},
        '7.1' : {},
        '8.0' : {},
        '8.0Exp' : {},
    }
    default_install_loc = install_locs['6.0']

class msvs6bTestCase(msvsTestCase):
    """Test Other MSVS 6 Registry"""
    registry = DummyRegistry(regdata_6b + regdata_cv)
    default_version = '6.0'
    highest_version = '6.0'
    number_of_versions = 1
    install_locs = {
        '6.0' : {'VSINSTALLDIR': 'C:\\VS6', 'VCINSTALLDIR': 'C:\\VS6\\VC98'},
        '7.0' : {},
        '7.1' : {},
        '8.0' : {},
        '8.0Exp' : {},
    }
    default_install_loc = install_locs['6.0']

class msvs6and7TestCase(msvsTestCase):
    """Test MSVS 6 & 7 Registry"""
    registry = DummyRegistry(regdata_6b + regdata_7 + regdata_cv)
    default_version = '7.0'
    highest_version = '7.0'
    number_of_versions = 2
    install_locs = {
        '6.0' : {'VSINSTALLDIR': 'C:\\VS6', 'VCINSTALLDIR': 'C:\\VS6\\VC98'},
        '7.0' : {'VSINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio .NET\\', 'VCINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio .NET\\Vc7\\'},
        '7.1' : {},
        '8.0' : {},
        '8.0Exp' : {},
    }
    default_install_loc = install_locs['7.0']

class msvs7TestCase(msvsTestCase):
    """Test MSVS 7 Registry"""
    registry = DummyRegistry(regdata_7 + regdata_cv)
    default_version = '7.0'
    highest_version = '7.0'
    number_of_versions = 1
    install_locs = {
        '6.0' : {'VSINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio'},
        '7.0' : {'VSINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio .NET\\', 'VCINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio .NET\\Vc7\\'},
        '7.1' : {},
        '8.0' : {},
        '8.0Exp' : {},
    }
    default_install_loc = install_locs['7.0']

class msvs71TestCase(msvsTestCase):
    """Test MSVS 7.1 Registry"""
    registry = DummyRegistry(regdata_7_1 + regdata_cv)
    default_version = '7.1'
    highest_version = '7.1'
    number_of_versions = 1
    install_locs = {
        '6.0' : {'VSINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio'},
        '7.0' : {},
        '7.1' : {'VSINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio .NET 2003\\', 'VCINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio .NET 2003\\Vc7\\'},
        '8.0' : {},
        '8.0Exp' : {},
    }
    default_install_loc = install_locs['7.1']

class msvs8ExpTestCase(msvsTestCase):
    """Test MSVS 8 Express Registry"""
    registry = DummyRegistry(regdata_8exp + regdata_cv)
    default_version = '8.0Exp'
    highest_version = '8.0Exp'
    number_of_versions = 1
    install_locs = {
        '6.0' : {'VSINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio'},
        '7.0' : {},
        '7.1' : {},
        '8.0' : {'VSINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio 8\\', 'VCINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio 8\\VC\\'},
        '8.0Exp' : {'VSINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio 8\\', 'VCINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio 8\\VC\\'},
    }
    default_install_loc = install_locs['8.0Exp']

class msvsEmptyTestCase(msvsTestCase):
    """Test Empty Registry"""
    registry = DummyRegistry(regdata_none)
    default_version = '6.0'
    highest_version = None
    number_of_versions = 0
    install_locs = {
        '6.0' : {'VSINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio'},
        '7.0' : {},
        '7.1' : {},
        '8.0' : {},
        '8.0Exp' : {},
    }
    default_install_loc = install_locs['8.0Exp']

if __name__ == "__main__":

    # only makes sense to test this on win32
    if sys.platform != 'win32':
        sys.stdout.write("NO RESULT for msvsTests.py:  '%s' is not win32\n" % sys.platform)
        sys.exit(0)

    SCons.Util.RegOpenKeyEx = DummyOpenKeyEx
    SCons.Util.RegEnumKey = DummyEnumKey
    SCons.Util.RegEnumValue = DummyEnumValue
    SCons.Util.RegQueryValueEx = DummyQueryValue
    os.path.exists = DummyExists # make sure all files exist :-)

    exit_val = 0

    test_classes = [
        msvs6aTestCase,
        msvs6bTestCase,
        msvs6and7TestCase,
        msvs7TestCase,
        msvs71TestCase,
        msvs8ExpTestCase,
        msvsEmptyTestCase,
    ]

    for test_class in test_classes:
        print test_class.__doc__
        suite = unittest.makeSuite(test_class, 'test_')
        if not unittest.TextTestRunner().run(suite).wasSuccessful():
            exit_val = 1

    sys.exit(exit_val)
