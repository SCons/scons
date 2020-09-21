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
import sys
import unittest
import copy

import TestCmd
import TestUnit

from SCons.Tool.msvs import *
from SCons.Tool.MSCommon.vs import SupportedVSList
import SCons.Node.FS
import SCons.Util
import SCons.Warnings

from SCons.Tool.MSCommon.common import debug

from SCons.Tool.MSCommon import get_default_version, \
                                query_versions
from SCons.Tool.msvs import _GenerateV6DSP, _GenerateV7DSP, _GenerateV10DSP

regdata_6a = r'''[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio]
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\6.0]
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\6.0\ServicePacks]
"sp3"=""
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\6.0\Setup]
"VsCommonDir"="C:\Program Files\Microsoft Visual Studio\Common"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\6.0\Setup\Microsoft Developer Network Library - Visual Studio 6.0a]
"ProductDir"="C:\Program Files\Microsoft Visual Studio\MSDN98\98VSa\1033"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\6.0\Setup\Microsoft Visual C++]
"ProductDir"="C:\Program Files\Microsoft Visual Studio\VC98"
'''.split('\n')

regdata_6b = r'''[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio]
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
'''.split('\n')

regdata_7 = r'''
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
'''.split('\n')

regdata_7_1 = r'''
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
'''.split('\n')

regdata_8exp = r'''
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
'''.split('\n')

regdata_80 = r'''
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\8.0]
"CLR Version"="v2.0.50727"
"ApplicationID"="VisualStudio"
"ThisVersionDTECLSID"="{BA018599-1DB3-44f9-83B4-461454C84BF8}"
"ThisVersionSolutionCLSID"="{1B2EEDD6-C203-4d04-BD59-78906E3E8AAB}"
"SecurityAppID"="{DF99D4F5-9F04-4CEF-9D39-095821B49C77}"
"InstallDir"="C:\Program Files\Microsoft Visual Studio 8\Common7\IDE\"
"EnablePreloadCLR"=dword:00000001
"RestoreAppPath"=dword:00000001
"Source Directories"="C:\Program Files\Microsoft Visual Studio 8\VC\crt\src\;C:\Program Files\Microsoft Visual Studio 8\VC\atlmfc\src\mfc\;C:\Program Files\Microsoft Visual Studio 8\VC\atlmfc\src\atl\;C:\Program Files\Microsoft Visual Studio 8\VC\atlmfc\include\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\8.0\InstalledProducts]
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\8.0\InstalledProducts\Microsoft Visual C++]
"UseInterface"=dword:00000001
"Package"="{F1C25864-3097-11D2-A5C5-00C04F7968B4}"
"DefaultProductAttribute"="VC"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\8.0\Setup]
"Dbghelp_path"="C:\Program Files\Microsoft Visual Studio 8\Common7\IDE\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\8.0\Setup\EF]
"ProductDir"="C:\Program Files\Microsoft Visual Studio 8\EnterpriseFrameworks\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\8.0\Setup\Microsoft Visual Studio 2005 Professional Edition - ENU]
"SrcPath"="d:\vs\"
"InstallSuccess"=dword:00000001
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\8.0\Setup\VC]
"ProductDir"="C:\Program Files\Microsoft Visual Studio 8\VC\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\8.0\Setup\VS]
"ProductDir"="C:\Program Files\Microsoft Visual Studio 8\"
"VS7EnvironmentLocation"="C:\Program Files\Microsoft Visual Studio 8\Common7\IDE\devenv.exe"
"EnvironmentPath"="C:\Program Files\Microsoft Visual Studio 8\Common7\IDE\devenv.exe"
"EnvironmentDirectory"="C:\Program Files\Microsoft Visual Studio 8\Common7\IDE\"
"VS7CommonDir"="C:\Program Files\Microsoft Visual Studio 8\Common7\"
"VS7CommonBinDir"="C:\Program Files\Microsoft Visual Studio 8\Common7\Tools\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\8.0\Setup\VS\BuildNumber]
"1033"="8.0.50727.42"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\8.0\Setup\VS\Pro]
"ProductDir"="C:\Program Files\Microsoft Visual Studio 8\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\8.0\VC]
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\8.0\VC\VC_OBJECTS_PLATFORM_INFO]
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\8.0\VC\VC_OBJECTS_PLATFORM_INFO\Win32]
@="{72f11281-2429-11d7-8bf6-00b0d03daa06}"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\8.0\VC\VC_OBJECTS_PLATFORM_INFO\Win32\ToolDefaultExtensionLists]
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
'''.split('\n')

regdata_140 = r'''
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\14.0\Setup\VS]
"MSMDir"="C:\\Program Files (x86)\\Common Files\\Merge Modules\\"
"ProductDir"="C:\\Program Files (x86)\\Microsoft Visual Studio 14.0\\"
"VS7EnvironmentLocation"="C:\\Program Files (x86)\\Microsoft Visual Studio 14.0\\Common7\\IDE\\devenv.exe"
"EnvironmentPath"="C:\\Program Files (x86)\\Microsoft Visual Studio 14.0\\Common7\\IDE\\devenv.exe"
"EnvironmentDirectory"="C:\\Program Files (x86)\\Microsoft Visual Studio 14.0\\Common7\\IDE\\"
"VS7CommonDir"="C:\\Program Files (x86)\\Microsoft Visual Studio 14.0\\Common7\\"
"VS7CommonBinDir"=""
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\14.0\Setup\VS\BuildNumber]
"1033"="14.0"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\14.0\Setup\VS\Community]
"ProductDir"="C:\\Program Files (x86)\\Microsoft Visual Studio 14.0\\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\14.0\Setup\VS\JSLS_MSI]
"Version"="14.0.25527"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\14.0\Setup\VS\JSPS_MSI]
"Version"="14.0.25527"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\14.0\Setup\VS\Pro]
"ProductDir"="C:\\Program Files (x86)\\Microsoft Visual Studio 14.0\\"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\14.0\Setup\VS\professional]
"IsInstallInProgress"="0"
"CurrentOperation"="install"
"SetupFeedUri"="http://go.microsoft.com/fwlink/?LinkID=659004&clcid=0x409"
"SetupFeedLocalCache"="C:\\ProgramData\\Microsoft\\VisualStudioSecondaryInstaller\\14.0\\LastUsedFeed\\{68432bbb-c9a5-4a7b-bab3-ae5a49b28303}\\Feed.xml"
"InstallResult"="0"
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\14.0\Setup\VS\SecondaryInstaller]
[HKEY_LOCAL_MACHINE\Software\Microsoft\VisualStudio\14.0\Setup\VS\SecondaryInstaller\AppInsightsTools]
"Version"="7.0.20620.1"
'''.split('\n')

regdata_cv = r'''[HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion]
"ProgramFilesDir"="C:\Program Files"
"CommonFilesDir"="C:\Program Files\Common Files"
"MediaPath"="C:\WINDOWS\Media"
'''.split('\n')


regdata_none = []

class DummyEnv:
    def __init__(self, dict=None):
        self.fs = SCons.Node.FS.FS()
        if dict:
            self.dict = dict
        else:
            self.dict = {}

    def Dictionary(self, key = None):
        if not key:
            return self.dict
        return self.dict[key]

    def __setitem__(self, key, value):
        self.dict[key] = value

    def __getitem__(self, key):
        return self.dict[key]

    def __contains__(self, key):
        return key in self.dict

    def has_key(self, name):
        return name in self.dict

    def get(self, name, value=None):
        if name in self.dict:
            return self.dict[name]
        else:
            return value

    def Dir(self, name):
        return self.fs.Dir(name)


class RegKey:
    """key class for storing an 'open' registry key"""
    def __init__(self,key):
        self.key = key

# Warning: this is NOT case-insensitive, unlike the Windows registry.
# So e.g. HKLM\Software is NOT the same key as HKLM\SOFTWARE.
class RegNode:
    """node in the dummy registry"""
    def __init__(self,name):
        self.valdict = {}
        self.keydict = {}
        self.keyarray = []
        self.valarray = []
        self.name = name

    def value(self,val):
        if val in self.valdict:
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
        if name.find(sep) != -1:
            keyname, subkeys = name.split(sep, 1)
        else:
            keyname = name
            subkeys = ""

        if keyname not in self.keydict:
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
        parents = [None, None]
        parents[0] = self.root
        keymatch = re.compile(r'^\[(.*)\]$')
        valmatch = re.compile(r'^(?:"(.*)"|[@])="(.*)"$')
        for line in data:
            m1 = keymatch.match(line)
            if m1:
                # add a key, set it to current parent.
                # Also create subkey for Wow6432Node of HKLM\Software;
                # that's where it looks on a 64-bit machine (tests will fail w/o this)
                parents[0] = self.root.addKey(m1.group(1))
                if 'HKEY_LOCAL_MACHINE\\Software' in m1.group(1):
                    p1 = m1.group(1).replace('HKEY_LOCAL_MACHINE\\Software', 'HKEY_LOCAL_MACHINE\\Software\\Wow6432Node')
                    parents[1] = self.root.addKey(p1)
                else:
                    parents[1] = None
            else:
                m2 = valmatch.match(line)
                if m2:
                    for p in parents:
                        if p:
                            p.addValue(m2.group(1),m2.group(2))

    def OpenKeyEx(self,root,key):
        if root == SCons.Util.HKEY_CLASSES_ROOT:
            mykey = 'HKEY_CLASSES_ROOT\\' + key
        if root == SCons.Util.HKEY_USERS:
            mykey = 'HKEY_USERS\\' + key
        if root == SCons.Util.HKEY_CURRENT_USER:
            mykey = 'HKEY_CURRENT_USER\\' + key
        if root == SCons.Util.HKEY_LOCAL_MACHINE:
            mykey = 'HKEY_LOCAL_MACHINE\\' + key
        debug("Open Key:%s"%mykey)
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

def DummyVsWhere(msvc_version, env):
    # not testing versions with vswhere, so return none
    return None

class msvsTestCase(unittest.TestCase):
    """This test case is run several times with different defaults.
    See its subclasses below."""
    def setUp(self):
        debug("THIS TYPE :%s"%self)
        global registry
        registry = self.registry
        from SCons.Tool.MSCommon.vs import reset_installed_visual_studios
        reset_installed_visual_studios()

        self.test = TestCmd.TestCmd(workdir='')
        # FS doesn't like the cwd to be something other than its root.
        os.chdir(self.test.workpath(""))
        self.fs = SCons.Node.FS.FS()

    def test_get_default_version(self):
        """Test retrieval of the default visual studio version"""

        debug("Testing for default version %s"%self.default_version)
        env = DummyEnv()
        v1 = get_default_version(env)
        if v1:
            assert env['MSVS_VERSION'] == self.default_version, \
                   ("env['MSVS_VERSION'] != self.default_version",
                    env['MSVS_VERSION'],self.default_version)
            assert env['MSVS']['VERSION'] == self.default_version, \
                   ("env['MSVS']['VERSION'] != self.default_version",
                    env['MSVS']['VERSION'], self.default_version)
            assert v1 == self.default_version, (self.default_version, v1)

        env = DummyEnv({'MSVS_VERSION':'7.0'})
        v2 = get_default_version(env)
        assert env['MSVS_VERSION'] == '7.0', env['MSVS_VERSION']
        assert env['MSVS']['VERSION'] == '7.0', env['MSVS']['VERSION']
        assert v2 == '7.0', v2

        env = DummyEnv()
        v3 = get_default_version(env)
        if v3 == '7.1':
            override = '7.0'
        else:
            override = '7.1'
        env['MSVS_VERSION'] = override
        v3 = get_default_version(env)
        assert env['MSVS_VERSION'] == override, env['MSVS_VERSION']
        assert env['MSVS']['VERSION'] == override, env['MSVS']['VERSION']
        assert v3 == override, v3

    def _TODO_test_merge_default_version(self):
        """Test the merge_default_version() function"""
        pass

    def test_query_versions(self):
        """Test retrieval of the list of visual studio versions"""
        v1 = query_versions()
        assert not v1 or str(v1[0]) == self.highest_version, \
               (v1, self.highest_version)
        assert len(v1) == self.number_of_versions, v1
        
    def test_config_generation(self):
        """Test _DSPGenerator.__init__(...)"""
        if not self.highest_version :
            return
        
        # Initialize 'static' variables
        version_num, suite = msvs_parse_version(self.highest_version)
        if version_num >= 10.0:
            function_test = _GenerateV10DSP
            suffix = '.vcxproj'
        elif version_num >= 7.0:
            function_test = _GenerateV7DSP
            suffix = '.dsp'
        else:
            function_test = _GenerateV6DSP
            suffix = '.dsp'

        # Avoid any race conditions between the test cases when we test
        # actually writing the files.
        dspfile = 'test%s%s' % (hash(self), suffix)
            
        str_function_test = str(function_test.__init__)
        source = 'test.cpp'
        
        # Create the cmdargs test list
        list_variant = ['Debug|Win32','Release|Win32',
                        'Debug|x64', 'Release|x64']
        list_cmdargs = ['debug=True target_arch=32', 
                        'debug=False target_arch=32',
                        'debug=True target_arch=x64', 
                        'debug=False target_arch=x64']
        list_cppdefines = [['_A', '_B', 'C'], ['_B', '_C_'], ['D'], []]
        list_cpppaths = [[r'C:\test1'], [r'C:\test1;C:\test2'],
                         [self.fs.Dir('subdir')], []]
        list_cppflags = [['/std:c++17', '/Zc:__cplusplus'],
                         ['/std:c++14', '/Zc:__cplusplus'],
                         ['/std:c++11', '/Zc:__cplusplus'], []]

        def TestParamsFromList(test_variant, test_list):
            """
            Generates test data based on the parameters passed in.

            Returns tuple list:
                1. Parameter.
                2. Dictionary of expected result per variant.
            """
            def normalizeParam(param):
                """
                Converts the raw data based into the AddConfig function of
                msvs.py to the expected result.

                Expects the following behavior:
                    1. A value of None will be converted to an empty list.
                    2. A File or Directory object will be converted to an
                       absolute path (because those objects can't be pickled).
                    3. Otherwise, the parameter will be used.
                """
                if param is None:
                    return []
                elif isinstance(param, list):
                    return [normalizeParam(p) for p in param]
                elif hasattr(param, 'abspath'):
                    return param.abspath
                else:
                    return param

            return [
                (None, dict.fromkeys(test_variant, '')),
                ('', dict.fromkeys(test_variant, '')),
                (test_list[0], dict.fromkeys(test_variant, normalizeParam(test_list[0]))),
                (test_list, dict(list(zip(test_variant, [normalizeParam(x) for x in test_list]))))
            ]

        tests_cmdargs = TestParamsFromList(list_variant, list_cmdargs)
        tests_cppdefines = TestParamsFromList(list_variant, list_cppdefines)
        tests_cpppaths = TestParamsFromList(list_variant, list_cpppaths)
        tests_cppflags = TestParamsFromList(list_variant, list_cppflags)

        # Run the test for each test case
        for param_cmdargs, expected_cmdargs in tests_cmdargs:
            for param_cppdefines, expected_cppdefines in tests_cppdefines:
                for param_cpppaths, expected_cpppaths in tests_cpppaths:
                    for param_cppflags, expected_cppflags in tests_cppflags:
                        print('Testing %s. with :\n  variant = %s \n  cmdargs = "%s" \n  cppdefines = "%s" \n  cpppaths = "%s" \n  cppflags = "%s"' % \
                              (str_function_test, list_variant, param_cmdargs, param_cppdefines, param_cpppaths, param_cppflags))
                        param_configs = []
                        expected_configs = {}
                        for platform in ['Win32', 'x64']:
                            for variant in ['Debug', 'Release']:
                                variant_platform = '%s|%s' % (variant, platform)
                                runfile = '%s\\%s\\test.exe' % (platform, variant)
                                buildtarget = '%s\\%s\\test.exe' % (platform, variant)
                                outdir = '%s\\%s' % (platform, variant)

                                # Create parameter list for this variant_platform
                                param_configs.append([variant_platform, runfile, buildtarget, outdir])

                                # Create expected dictionary result for this variant_platform
                                expected_configs[variant_platform] = {
                                    'variant': variant,
                                    'platform': platform,
                                    'runfile': runfile,
                                    'buildtarget': buildtarget,
                                    'outdir': outdir,
                                    'cmdargs': expected_cmdargs[variant_platform],
                                    'cppdefines': expected_cppdefines[variant_platform],
                                    'cpppaths': expected_cpppaths[variant_platform],
                                    'cppflags': expected_cppflags[variant_platform],
                                }

            # Create parameter environment with final parameter dictionary
            param_dict = dict(list(zip(('variant', 'runfile', 'buildtarget', 'outdir'),
                                  [list(l) for l in zip(*param_configs)])))
            param_dict['cmdargs'] = param_cmdargs
            param_dict['cppdefines'] = param_cppdefines
            param_dict['cpppaths'] = param_cpppaths
            param_dict['cppflags'] = param_cppflags

            # Hack to be able to run the test with a 'DummyEnv'
            class _DummyEnv(DummyEnv):
                def subst(self, string, *args, **kwargs):
                    return string
            
            env = _DummyEnv(param_dict)
            env['MSVSSCONSCRIPT'] = ''
            env['MSVS_VERSION'] = self.highest_version
            env['MSVSBUILDTARGET'] = 'target'
           
            # Call function to test
            genDSP = function_test(dspfile, source, env)
        
            # Check expected result
            self.assertListEqual(list(genDSP.configs.keys()), list(expected_configs.keys()))
            for key, v in genDSP.configs.items():
                self.assertDictEqual(v.__dict__, expected_configs[key])

            genDSP.Build()

            # Delete the resulting file so we don't leave anything behind.
            for file in [dspfile, dspfile + '.filters']:
                path = os.path.realpath(file)
                try:
                    os.remove(path)
                except OSError:
                    pass

class msvs6aTestCase(msvsTestCase):
    """Test MSVS 6 Registry"""
    registry = DummyRegistry(regdata_6a + regdata_cv)
    default_version = '6.0'
    highest_version = '6.0'
    number_of_versions = 1
    install_locs = {
        '6.0' : {'VSINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio\\VC98', 'VCINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio\\VC98\\Bin'},
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
        '6.0' : {'VSINSTALLDIR': 'C:\\VS6\\VC98', 'VCINSTALLDIR': 'C:\\VS6\\VC98\\Bin'},
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
        '6.0' : {'VSINSTALLDIR': 'C:\\VS6\\VC98',
                 'VCINSTALLDIR': 'C:\\VS6\\VC98\\Bin'},
        '7.0' : {'VSINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio .NET\\Common7',
                 'VCINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio .NET\\Common7\\Tools'},
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
        '6.0' : {},
        '7.0' : {'VSINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio .NET\\Common7',
                 'VCINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio .NET\\Common7\\Tools'},
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
        '6.0' : {},
        '7.0' : {},
        '7.1' : {'VSINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio .NET 2003\\Common7',
                 'VCINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio .NET 2003\\Common7\\Tools'},
        '8.0' : {},
        '8.0Exp' : {},
    }
    default_install_loc = install_locs['7.1']

class msvs8ExpTestCase(msvsTestCase): # XXX: only one still not working
    """Test MSVS 8 Express Registry"""
    registry = DummyRegistry(regdata_8exp + regdata_cv)
    default_version = '8.0Exp'
    highest_version = '8.0Exp'
    number_of_versions = 1
    install_locs = {
        '6.0' : {},
        '7.0' : {},
        '7.1' : {},
        '8.0' : {},
        '8.0Exp' : {'VSINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio 8',
                    'VCINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio 8\\VC'},
    }
    default_install_loc = install_locs['8.0Exp']

class msvs80TestCase(msvsTestCase):
    """Test MSVS 8 Registry"""
    registry = DummyRegistry(regdata_80 + regdata_cv)
    default_version = '8.0'
    highest_version = '8.0'
    number_of_versions = 1
    install_locs = {
        '6.0' : {},
        '7.0' : {},
        '7.1' : {},
        '8.0' : {'VSINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio 8',
                 'VCINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio 8\\VC'},
        '8.0Exp' : {},
    }
    default_install_loc = install_locs['8.0']

class msvs140TestCase(msvsTestCase):
    """Test MSVS 140 Registry"""
    registry = DummyRegistry(regdata_140 + regdata_cv)
    default_version = '14.0'
    highest_version = '14.0'
    number_of_versions = 2
    install_locs = {
        '14.0' : {'VSINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio 14.0',
                  'VCINSTALLDIR': 'C:\\Program Files\\Microsoft Visual Studio 14.0\\VC'},
    }
    default_install_loc = install_locs['14.0']

class msvsEmptyTestCase(msvsTestCase):
    """Test Empty Registry"""
    registry = DummyRegistry(regdata_none)
    default_version = SupportedVSList[0].version
    highest_version = None
    number_of_versions = 0
    install_locs = {
        '6.0' : {},
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

    SCons.Util.RegOpenKeyEx    = DummyOpenKeyEx
    SCons.Util.RegEnumKey      = DummyEnumKey
    SCons.Util.RegEnumValue    = DummyEnumValue
    SCons.Util.RegQueryValueEx = DummyQueryValue
    SCons.Tool.MSCommon.vc.find_vc_pdir_vswhere = DummyVsWhere

    os.path.exists = DummyExists # make sure all files exist :-)
    os.path.isfile = DummyExists # make sure all files are files :-)
    os.path.isdir  = DummyExists # make sure all dirs are dirs :-)

    exit_val = 0

    test_classes = [
        msvs6aTestCase,
        msvs6bTestCase,
        msvs6and7TestCase,
        msvs7TestCase,
        msvs71TestCase,
        msvs8ExpTestCase,
        msvs80TestCase,
        msvs140TestCase,
        msvsEmptyTestCase,
    ]

    for test_class in test_classes:
        print("TEST: ", test_class.__doc__)
        back_osenv = copy.deepcopy(os.environ)
        try:
            # XXX: overriding the os.environ is bad, but doing it
            # correctly is too complicated for now. Those tests should
            # be fixed
            for k in ['VS71COMNTOOLS',
                      'VS80COMNTOOLS',
                      'VS90COMNTOOLS']:
                if k in os.environ:
                    del os.environ[k]

            suite = unittest.makeSuite(test_class, 'test_')
            if not TestUnit.cli.get_runner()().run(suite).wasSuccessful():
                exit_val = 1
        finally:
            os.env = back_osenv

    sys.exit(exit_val)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
