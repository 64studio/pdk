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

from distutils.core import setup

# Install pdk.test for now, so that pylint will automatically
# check the unit tests also.

# In the future we may want to leave pdk.test out of this, as it
# isn't actually needed at runtime.

setup(name="pdk",
      scripts=["bin/pdk", "bin/picax", "utest.py", "picax-utest.py"],
      packages=["pdk", "picax", "picax.modules", "pdk.test", "picax.test"],
      py_modules=["hashfile"])

# vim:set ai et sw=4 ts=4 tw=75:
