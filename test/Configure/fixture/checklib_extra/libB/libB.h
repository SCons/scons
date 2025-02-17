// SPDX-License-Identifier: MIT
//
// Copyright The SCons Foundation

#ifndef _LIBB_H
#define _LIBB_H

// define BUILDINGSHAREDLIB when building libB as shared lib
#ifdef _MSC_VER
# ifdef BUILDINGSHAREDLIB
#  define LIBB_DECL __declspec(dllexport)
# else
#  define LIBB_DECL __declspec(dllimport)
# endif
#endif // WIN32

#ifndef LIBB_DECL
# define LIBB_DECL
#endif

LIBB_DECL void libB(void);
#endif // _LIBB_H
