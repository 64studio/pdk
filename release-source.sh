#!/bin/sh
#
# $Progeny$
#
#   Copyright 2006 Progeny Linux Systems, Inc.
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

# This script builds, installs, and runs acceptance tests for a package
# build.

# Usage:
#
# ./release-source.sh <version>
#
# where <version> is the git tag you want to release

set -e
set -x

tag="$1"

export_base=$tag

git archive --format=tar --worktree-attributes --prefix=pdk-$tag/ $tag | gzip > pdk_$tag.tar.gz

# vim:set ai et sw=4 ts=4 tw=75:
