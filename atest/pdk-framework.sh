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

# Check the general soundness of the pdk command framework.

#None of these help calls should result in a crash
#(meaningful help is another question altogether)
pdk commit --help
pdk workspace create --help
pdk help
pdk help commit
pdk help commit foo
pdk help workspace
pdk help workspace foo && fail 'Should have failed.'
pdk help workspace foo fighters && fail 'Should have failed'
pdk help workspace create
pdk help workspace create foo

pdk workspace && fail 'Should have failed.'
pdk workspace zippo && fail 'Should have failed.'

# vim:set ai et sw=4 ts=4 tw=75:
