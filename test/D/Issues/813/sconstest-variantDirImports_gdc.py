#!/usr/bin/env python
#
# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

"""Test issue #813 (VariantDir imports) with the gdc tool."""

from Common.variantDirImports import testForTool

testForTool('gdc')
