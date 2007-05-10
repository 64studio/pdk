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

set -e
set -x

tag="$1"
version=$(echo $tag | awk -v FS=- '{print $2}')

if [ -z "$version" ]; then
    echo >&2 "Can't parse version from tag."
    exit 1
fi

export_base=$tag
git tar-tree $tag $export_base | gzip > pdk_$version.tar.gz

# vim:set ai et sw=4 ts=4 tw=75:
