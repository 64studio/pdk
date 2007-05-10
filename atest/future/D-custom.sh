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

##D) Creating a "Custom" Product
##   The developer
##   1. performs items "A" and "B"
##   2. modifies to the descriptor hierarchy
##   3. verifies "correctness" of changes (or corrects)
##   4. generates a repo

# get Utility functions
. atest/test_lib.sh

## steps 1 and 2 are assumed done setting up our test environment
pdk download
##need some examination to verify presence of the correct descriptors
##replace on of the acquired descriptors with a local copy that is slightly different, to represent an edit
pdk apply
pdk repogen

# vim:set ai et sw=4 ts=4 tw=75:
