# ------------------------------------------------------------------
# Copyright (c) 2021 PyInstaller Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

import glob
import os
import shutil

from PyInstaller.compat import is_win, is_darwin

binaries = []
datas = []

# List of binaries agraph.py may invoke.
progs = [
    "neato",
    "dot",
    "twopi",
    "circo",
    "fdp",
    "nop",
    "acyclic",
    "gvpr",
    "gvcolor",
    "ccomps",
    "sccmap",
    "tred",
    "sfdp",
    "unflatten",
]

if is_darwin:
    # The dot binary in PATH is typically a symlink, handle that.
    # graphviz_bindir is e.g. /usr/local/Cellar/graphviz/2.46.0/bin
    graphviz_bindir = os.path.dirname(os.path.realpath(shutil.which("dot")))
    for binary in progs:
        binaries.append((graphviz_bindir + "/" + binary, "."))
    # graphviz_bindir is e.g. /usr/local/Cellar/graphviz/2.46.0/lib/graphviz
    graphviz_libdir = os.path.realpath(graphviz_bindir + "/../lib/graphviz")
    for binary in glob.glob(graphviz_libdir + "/*.dylib"):
        binaries.append((binary, "graphviz"))
    for data in glob.glob(graphviz_libdir + "/config*"):
        datas.append((data, "graphviz"))

if is_win:
    for prog in progs:
        for binary in glob.glob("c:/Program Files/Graphviz*/bin/" + prog + ".exe"):
            binaries.append((binary, "."))
    for binary in glob.glob("c:/Program Files/Graphviz*/bin/*.dll"):
        binaries.append((binary, "."))
    for data in glob.glob("c:/Program Files/Graphviz*/bin/config*"):
        datas.append((data, "."))
