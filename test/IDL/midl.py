#!/usr/bin/env python
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

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re)

test.skip_if_not_msvc()

#####
# Test the basics

test.write('SConstruct',"""
import os

env = Environment(CPPPATH = '${TARGET.dir}',
                  tools = ['mssdk', 'msvc', 'mslink', 'midl'])
Export('env')

VariantDir('build', 'src')
SConscript(os.path.join('build','SConscript'))

VariantDir('build2', 'src', duplicate=0)
SConscript(os.path.join('build2','SConscript'))
""")

test.subdir('src','build')

test.write('src/SConscript',"""
Import('env')

local = env.Clone(WINDOWS_INSERT_DEF = 1)

barsrc = [
    'BarObject.cpp',
    'BarPCH.obj',
    'bar.cpp',
    local.RES('bar.rc', RCFLAGS= '/I${SOURCE.srcdir}'),
    ]

local.TypeLibrary('bar.idl')

local.SharedLibrary(target = 'bar.dll',
                    source = barsrc,
                    PCH=local.PCH('BarPCH.cpp', CXXFLAGS='/nologo')[0],
                    PCHSTOP = 'BarPCH.h',
                    register=0) # can't test registration, Win7 requires elevation for that.
""")

test.write('src/BarObject.cpp','''
#include "BarPCH.h"
#include "Bar.h"
#include "BarObject.h"
''')

test.write('src/BarObject.h','''
#ifndef __BAROBJECT_H_
#define __BAROBJECT_H_

#include "resource.h"

class ATL_NO_VTABLE CBarObject : 
        public CComObjectRootEx<CComSingleThreadModel>,
        public CComCoClass<CBarObject, &CLSID_BarObject>,
        public IDispatchImpl<IBarObject, &IID_IBarObject, &LIBID_BARLib>
{
public:
        CBarObject()
        {
        }

DECLARE_REGISTRY_RESOURCEID(IDR_BAROBJECT)

DECLARE_PROTECT_FINAL_CONSTRUCT()

BEGIN_COM_MAP(CBarObject)
        COM_INTERFACE_ENTRY(IBarObject)
        COM_INTERFACE_ENTRY(IDispatch)
END_COM_MAP()

public:
};

#endif
''')

test.write('src/BarObject.rgs',"""
HKCR
{
        Bar.BarObject.1 = s 'BarObject Class'
        {
                CLSID = s '{640BE9EC-B79D-4C9E-BB64-95D24854A303}'
        }
        Bar.BarObject = s 'BarObject Class'
        {
                CLSID = s '{640BE9EC-B79D-4C9E-BB64-95D24854A303}'
                CurVer = s 'Bar.BarObject.1'
        }
        NoRemove CLSID
        {
                ForceRemove {640BE9EC-B79D-4C9E-BB64-95D24854A303} = s 'BarObject Class'
                {
                        ProgID = s 'Bar.BarObject.1'
                        VersionIndependentProgID = s 'Bar.BarObject'
                        ForceRemove 'Programmable'
                        InprocServer32 = s '%MODULE%'
                        {
                                val ThreadingModel = s 'Apartment'
                        }
                        'TypeLib' = s '{73E5EA5F-9D45-463F-AA33-9F376AF7B643}'
                }
        }
}
""")

test.write('src/BarPCH.cpp','''
#include "BarPCH.h"

// #ifdef _ATL_STATIC_REGISTRY
// #include <statreg.h>
// #include <statreg.cpp>
// #endif

// #include <atlimpl.cpp>
''')

test.write('src/BarPCH.h','''
#ifndef BarPCH_h
#define BarPCH_h

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#define STRICT
#ifndef _WIN32_WINNT
#define _WIN32_WINNT 0x0501
#endif
#define _ATL_APARTMENT_THREADED

#include <atlbase.h>
extern CComModule _Module;
#include <atlcom.h>

#endif
''')

test.write('src/bar.cpp','''
#include "BarPCH.h"
#include "resource.h"
#include <initguid.h>
#include "bar.h"

#include "bar_i.c"
#include "BarObject.h"

CComModule _Module;

BEGIN_OBJECT_MAP(ObjectMap)
OBJECT_ENTRY(CLSID_BarObject, CBarObject)
END_OBJECT_MAP()

extern "C"
BOOL WINAPI DllMain(HINSTANCE hInstance, DWORD dwReason, LPVOID lpReserved)
{
    lpReserved;
    if (dwReason == DLL_PROCESS_ATTACH)
    {
        _Module.Init(ObjectMap, hInstance, &LIBID_BARLib);
        DisableThreadLibraryCalls(hInstance);
    }
    else if (dwReason == DLL_PROCESS_DETACH)
        _Module.Term();
    return TRUE;    // ok
}

STDAPI DllCanUnloadNow(void)
{
    return (_Module.GetLockCount()==0) ? S_OK : S_FALSE;
}

STDAPI DllGetClassObject(REFCLSID rclsid, REFIID riid, LPVOID* ppv)
{
    return _Module.GetClassObject(rclsid, riid, ppv);
}

STDAPI DllRegisterServer(void)
{
    return _Module.RegisterServer(TRUE);
}

STDAPI DllUnregisterServer(void)
{
    return _Module.UnregisterServer(TRUE);
}
''')

test.write('src/bar.def','''
; bar.def : Declares the module parameters.

LIBRARY      "bar.DLL"

EXPORTS
        DllCanUnloadNow      PRIVATE
        DllGetClassObject    PRIVATE
        DllRegisterServer    PRIVATE
        DllUnregisterServer  PRIVATE
''')

test.write('src/bar.idl','''
import "oaidl.idl";
import "ocidl.idl";
        [
                object,
                uuid(22995106-CE26-4561-AF1B-C71C6934B840),
                dual,
                helpstring("IBarObject Interface"),
                pointer_default(unique)
        ]
        interface IBarObject : IDispatch
        {
        };

[
        uuid(73E5EA5F-9D45-463F-AA33-9F376AF7B643),
        version(1.0),
        helpstring("bar 1.0 Type Library")
]
library BARLib
{
        importlib("stdole32.tlb");
        importlib("stdole2.tlb");

        [
                uuid(640BE9EC-B79D-4C9E-BB64-95D24854A303),
                helpstring("BarObject Class")
        ]
        coclass BarObject
        {
                [default] interface IBarObject;
        };
};
''')

test.write('src/bar.rc','''
#include "resource.h"

#define APSTUDIO_READONLY_SYMBOLS

#include "winres.h"

#undef APSTUDIO_READONLY_SYMBOLS

#if !defined(AFX_RESOURCE_DLL) || defined(AFX_TARG_ENU)
#ifdef _WIN32
LANGUAGE LANG_ENGLISH, SUBLANG_ENGLISH_US
#pragma code_page(1252)
#endif //_WIN32

#ifdef APSTUDIO_INVOKED

1 TEXTINCLUDE DISCARDABLE 
BEGIN
    "resource.h\\0"
END

2 TEXTINCLUDE DISCARDABLE 
BEGIN
    "#include ""winres.h""\\r\\n"
    "\\0"
END

3 TEXTINCLUDE DISCARDABLE 
BEGIN
    "1 TYPELIB ""bar.tlb""\\r\\n"
    "\\0"
END

#endif    // APSTUDIO_INVOKED


#ifndef _MAC

VS_VERSION_INFO VERSIONINFO
 FILEVERSION 1,0,0,1
 PRODUCTVERSION 1,0,0,1
 FILEFLAGSMASK 0x3fL
#ifdef _DEBUG
 FILEFLAGS 0x1L
#else
 FILEFLAGS 0x0L
#endif
 FILEOS 0x4L
 FILETYPE 0x2L
 FILESUBTYPE 0x0L
BEGIN
    BLOCK "StringFileInfo"
    BEGIN
        BLOCK "040904B0"
        BEGIN
            VALUE "CompanyName", "\\0"
            VALUE "FileDescription", "bar Module\\0"
            VALUE "FileVersion", "1, 0, 0, 1\\0"
            VALUE "InternalName", "bar\\0"
            VALUE "LegalCopyright", "Copyright 2003\\0"
            VALUE "OriginalFilename", "bar.DLL\\0"
            VALUE "ProductName", "bar Module\\0"
            VALUE "ProductVersion", "1, 0, 0, 1\\0"
            VALUE "OLESelfRegister", "\\0"
        END
    END
    BLOCK "VarFileInfo"
    BEGIN
        VALUE "Translation", 0x409, 1200
    END
END

#endif    // !_MAC

IDR_BAROBJECT           REGISTRY DISCARDABLE    "BarObject.rgs"

STRINGTABLE DISCARDABLE 
BEGIN
    IDS_PROJNAME            "bar"
END

#endif    // English (U.S.) resources

#ifndef APSTUDIO_INVOKED

1 TYPELIB "bar.tlb"

#endif    // not APSTUDIO_INVOKED
''')

test.write('src/resource.h','''
#define IDS_PROJNAME                    100
#define IDR_BAROBJECT                   101

#ifdef APSTUDIO_INVOKED
#ifndef APSTUDIO_READONLY_SYMBOLS
#define _APS_NEXT_RESOURCE_VALUE        201
#define _APS_NEXT_COMMAND_VALUE         32768
#define _APS_NEXT_CONTROL_VALUE         201
#define _APS_NEXT_SYMED_VALUE           102
#endif
#endif
''')

test.run(arguments=os.path.join('build','bar.dll'))

test.must_exist(['build','BarPCH.pch'])
test.must_exist(['build','BarPCH.obj'])
test.must_exist(['build','bar.tlb'])
test.must_exist(['build','bar.h'])
test.must_exist(['build','bar_i.c'])
test.must_exist(['build','bar_p.c'])
test.must_exist(['build','bar_data.c'])
test.must_exist(['build','BarObject.obj'])
test.must_exist(['build','bar.obj'])
test.must_exist(['build','bar.res'])
test.must_exist(['build','bar.dll'])
test.must_exist(['build','bar.lib'])
test.must_exist(['build','bar.exp'])

test.run(arguments='-c .')

test.must_not_exist(['build','BarPCH.pch'])
test.must_not_exist(['build','BarPCH.obj'])
test.must_not_exist(['build','bar.tlb'])
test.must_not_exist(['build','bar.h'])
test.must_not_exist(['build','bar_i.c'])
test.must_not_exist(['build','bar_p.c'])
test.must_not_exist(['build','bar_data.c'])
test.must_not_exist(['build','BarObject.obj'])
test.must_not_exist(['build','bar.obj'])
test.must_not_exist(['build','bar.res'])
test.must_not_exist(['build','bar.dll'])
test.must_not_exist(['build','bar.lib'])
test.must_not_exist(['build','bar.exp'])

test.run(arguments=os.path.join('build2','bar.dll'))

test.must_exist(['build2','BarPCH.pch'])
test.must_exist(['build2','BarPCH.obj'])
test.must_exist(['build2','bar.tlb'])
test.must_exist(['build2','bar.h'])
test.must_exist(['build2','bar_i.c'])
test.must_exist(['build2','bar_p.c'])
test.must_exist(['build2','bar_data.c'])
test.must_exist(['build2','BarObject.obj'])
test.must_exist(['build2','bar.obj'])
test.must_exist(['build2','bar.res'])
test.must_exist(['build2','bar.dll'])
test.must_exist(['build2','bar.lib'])
test.must_exist(['build2','bar.exp'])

test.run(arguments='-c .')

test.must_not_exist(['build2','BarPCH.pch'])
test.must_not_exist(['build2','BarPCH.obj'])
test.must_not_exist(['build2','bar.tlb'])
test.must_not_exist(['build2','bar.h'])
test.must_not_exist(['build2','bar_i.c'])
test.must_not_exist(['build2','bar_p.c'])
test.must_not_exist(['build2','bar_data.c'])
test.must_not_exist(['build2','BarObject.obj'])
test.must_not_exist(['build2','bar.obj'])
test.must_not_exist(['build2','bar.res'])
test.must_not_exist(['build2','bar.dll'])
test.must_not_exist(['build2','bar.lib'])
test.must_not_exist(['build2','bar.exp'])

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
