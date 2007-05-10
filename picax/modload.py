# $Progeny$
#
# Code for loading modules.
#
#   Copyright 2003, 2004, 2005 Progeny Linux Systems, Inc.
#
#   This file is part of PDK.
#
#   PDK is free software; you can redistribute it and/or modify it
#   under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   PDK is distributed in the hope that it will be useful, but WITHOUT
#   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#   or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
#   License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with PDK; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

"""This module does the heavy lifting of importing external modules for
the installer and media subsystems."""

import sys

def load_module(name, module_dir = None):
    """Load the named module, optionally adding a module directory to the
    path."""

    if module_dir:
        sys.path.append(module_dir)

    inst_toplevel = None
    for parent_module in ("picax.modules", "picax_modules"):
        try:
            full_name = parent_module + "." + name
            inst_toplevel = __import__(full_name)
            break
        except ImportError:
            continue

    if not inst_toplevel:
        raise ImportError, "could not find module for %s" % (name,)

    if hasattr(inst_toplevel, name):
        inst = getattr(inst_toplevel, name)
    elif hasattr(inst_toplevel, "modules") and \
         hasattr(inst_toplevel.modules, name):
        inst = getattr(inst_toplevel.modules, name)
    else:
        raise ImportError, "cannot find modules for %s" % (name,)

    return inst

# vim:set ai et sw=4 ts=4 tw=75:
