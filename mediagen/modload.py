#
# Code for loading modules.
#
#   Copyright 2017 Chris Obbard <chris@64studio.com>
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
the output creation subsystems."""

import importlib
import sys

def load_output_script(class_name):
    return load_module(class_name, "mediagen.outputs")

def load_module(name, module_name):
    """Load a module."""
    full_name = module_name + "." + name
    module = importlib.import_module(full_name)
    return module