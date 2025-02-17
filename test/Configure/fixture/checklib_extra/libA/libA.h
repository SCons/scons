// SPDX-License-Identifier: MIT
//
// Copyright The SCons Foundation

#ifndef _LIBA_H
#define _LIBA_H

// define BUILDINGSHAREDLIB when building libA as shared lib
#ifdef _MSC_VER
# ifdef BUILDINGSHAREDLIB
#  define LIBA_DECL __declspec(dllexport)
# else
#  define LIBA_DECL __declspec(dllimport)
# endif
#endif // WIN32

#ifndef LIBA_DECL
# define LIBA_DECL
#endif

LIBA_DECL void libA(void);
#endif // _LIBA_H
