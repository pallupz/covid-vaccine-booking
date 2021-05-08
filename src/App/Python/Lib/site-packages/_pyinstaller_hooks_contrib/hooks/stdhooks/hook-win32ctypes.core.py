# ------------------------------------------------------------------
# Copyright (c) 2020 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

from PyInstaller.utils.hooks import exec_statement, collect_submodules

# We need to collect submodules from win32ctypes.core.cffi or
# win32ctypes.core.ctypes for win32ctypes.core to work. The use of
# the backend is determined by availability of cffi.
cffi_available = exec_statement(
    """try:import cffi;print('\\nTrue')\nexcept: print('\\nFalse')"""
).split()[-1] == 'True'

if cffi_available:
    hiddenimports = collect_submodules('win32ctypes.core.cffi')
else:
    hiddenimports = collect_submodules('win32ctypes.core.ctypes')
