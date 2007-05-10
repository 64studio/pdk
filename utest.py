# $Progeny$
#
#   Copyright 2005 Progeny Linux Systems, Inc.
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

"Test runner for the PDK unit tests."

import unittest

from pdk.test.test_package import *
from pdk.test.test_compile import *
from pdk.test.test_util import *
from pdk.test.test_component import *
from pdk.test.test_cache import *
from pdk.test.test_audit import *
from pdk.test.test_channels import *
from pdk.test.test_rules import *
from pdk.test.test_component_tree_builder import *
from pdk.test.test_diff import *
from pdk.test.test_progress import *
from pdk.test.test_meta import *
from pdk.test.test_index_file import *
from pdk.test.test_debish_condition import *
from pdk.test.test_media import *
from pdk.test.test_commands import *

if __name__ == "__main__":
    unittest.main()

# vim:set ai et sw=4 ts=4 tw=75:
