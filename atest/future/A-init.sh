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

##A) Initializing the Client Installation
##   The Developer:
##   1. acquires a Platform/PDK Bundle from Progeny (includes sample distro)
##   2. registers PDK as an evaluation copy (executes trial subscription and development license)
##   3. selects and "downloads" a product
##
##As a result, the client machine contains:
##      - the pdk toolkit
##      - a pdk file cache
##      - the descriptor files that comprise the selected product

# get Utility functions
. atest/test_lib.sh

## steps 1 and 2 are assumed done setting up our test environment
pdk download
##need some examination to verify presence of the correct descriptors

# vim:set ai et sw=4 ts=4 tw=75:
