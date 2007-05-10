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

##C) Acquiring updates from Progeny
##   The developer
##   1. performs items "A" and "B"
##   2. interrogates pdk for updates available on some scope
##      (Entire "system"? Product? Directory of components?)
##   3a. fully applies updates to some scope.  *or*
##   3b. uses a step-wise process to allow component-by-component
##       manual review of changes prior to appication.
##   4. generates a repo

# get Utility functions
. atest/test_lib.sh

pdk download
pdk repogen
##some kind of examination of the system at this state
pdk update
pdk add packages
pdk mark
pdk apply
pdk repogen
##some examination of state

# vim:set ai et sw=4 ts=4 tw=75:
