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

from PyInstaller.utils.hooks import is_module_satisfies, collect_submodules

hiddenimports = collect_submodules('markdown.extensions')

# Markdown 3.3 introduced markdown.htmlparser submodule with hidden
# dependency on html.parser
if is_module_satisfies("markdown >= 3.3"):
    hiddenimports += ['html.parser']
