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

# Make sure that the "default" deb repo layout works ok.

. atest/utils/repogen-fixture.sh

set_up_repogen_fixture test-repogen
cd test-repogen

pdk repogen progeny.com/apache.xml
find repo

[ -d './repo' ] || fail "mising repo directory"

# Check that the cache contains the files (pre-calculated sha1)
check_file "b7d31cf9a160c3aadaf5f1cd86cdc8762b3d4b1b" \
    "./repo/pool/main/a/apache2/apache2-common_2.0.53-5_i386.deb"
check_file "9d26152e78ca33a3d435433c67644b52ae4c670c" \
    "./repo/pool/main/a/apache2/apache2_2.0.53-5.dsc"
check_file "9f4be3925441f006f8ee2054d96303cdcdac9b0a" \
    "./repo/pool/main/a/apache2/apache2_2.0.53-5.diff.gz"
check_file "214867c073d2bd43ed8374c9f34fa5532a9d7de0" \
    "./repo/pool/main/a/apache2/apache2_2.0.53.orig.tar.gz"


# Ensure we have indices in all the places we expect them
assert_exists repo/dists/apache/Release
assert_exists repo/dists/apache/main/binary-i386/Release
assert_exists repo/dists/apache/main/source/Release

# Check for existance of tar.gz indices
assert_exists repo/dists/apache/main/binary-i386/Packages.gz
assert_exists repo/dists/apache/main/source/Sources.gz

repo_path=repo/pool/main/a/apache2

# Check all the binary files (heh, all one of them -- for now)
pkgname=apache2-common_2.0.53-5_i386.deb
grep ${pkgname} repo/dists/apache/main/binary-i386/Packages
assert_exists ${repo_path}/${pkgname}

# Check all the source files
for pkgname in apache2_2.0.53-5.diff.gz  \
               apache2_2.0.53-5.dsc  \
               apache2_2.0.53.orig.tar.gz; do
    grep ${pkgname} repo/dists/apache/main/source/Sources
    assert_exists ${repo_path}/${pkgname}
done

# vim:set ai et sw=4 ts=4 tw=75:
