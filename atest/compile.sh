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

# repogen works. Make sure the resulting repo looks sane. Packages
# in the repo should be hard linked to the cache.

. atest/utils/repogen-fixture.sh

set_up_repogen_fixture test-repogen
cd test-repogen

# should still work from a subdirectory
mkdir tmp
cd tmp
pdk repogen ../product.xml
cd -

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

check_file "a5b9ebe5914fa4fa2583b1f5eb243ddd90e6fbbe" \
    "./repo/pool/contrib/i/ida/ida_2.01-1.2_arm.deb"
check_file "48c0c56acbeb90f06be38da82f194c63d937b9a8" \
    "./repo/pool/contrib/i/ida/ida_2.01-1.2.diff.gz"
check_file "5758b8cd6b604e872d60a257777cc9d3018c84c8" \
    "./repo/pool/contrib/i/ida/ida_2.01-1.2.dsc"
check_file "000874ad1e2bbf975b5eb157e8d2e4dbe87cb006" \
    "./repo/pool/contrib/i/ida/ida_2.01.orig.tar.gz"


# Ensure we have indices in all the places we expect them
assert_exists repo/dists/stable/Release
assert_exists repo/dists/stable/main/binary-i386/Release
assert_exists repo/dists/stable/main/source/Release
assert_exists repo/dists/stable/contrib/binary-arm/Release
assert_exists repo/dists/stable/contrib/source/Release

assert_gzipped_matches () {
    local uncompressed_file=$1
    local gzipped_file=${uncompressed_file}.gz
    assert_exists $uncompressed_file
    assert_exists $gzipped_file

    gunzip <$gzipped_file | diff -u $uncompressed_file - \
        || fail 'uncompressed and gzipped content should match'
}

# Check for existance of tar.gz indices
assert_gzipped_matches repo/dists/stable/main/binary-i386/Packages
assert_gzipped_matches repo/dists/stable/main/source/Sources
assert_gzipped_matches repo/dists/stable/contrib/binary-arm/Packages
assert_gzipped_matches repo/dists/stable/contrib/source/Sources

repo_path=repo/pool/main/a/apache2

# Check all the apache binary files
pkgname=apache2-common_2.0.53-5_i386.deb
grep ${pkgname} repo/dists/stable/main/binary-i386/Packages
assert_exists ${repo_path}/${pkgname}

# Check for the MD5Sum header
grep "^MD5Sum: 5acd04d4cc6e9d1530aad04accdc8eb5" \
    repo/dists/stable/main/binary-i386/Packages \
    || fail "MD5Sum line not present or incorrect"

# Check all the apache source files
for filename in apache2_2.0.53-5.diff.gz  \
               apache2_2.0.53-5.dsc  \
               apache2_2.0.53.orig.tar.gz; do
    grep ${filename} repo/dists/stable/main/source/Sources
    assert_exists ${repo_path}/${filename}
done

repo_path=repo/pool/contrib/i/ida

# Check all the ida binary files
pkgname=ida_2.01-1.2_arm.deb
grep ${pkgname} repo/dists/stable/contrib/binary-arm/Packages
assert_exists ${repo_path}/${pkgname}

# Check all the ida source files
for filename in ida_2.01-1.2.dsc \
               ida_2.01-1.2.diff.gz \
               ida_2.01.orig.tar.gz; do
    grep ${filename} repo/dists/stable/contrib/source/Sources
    assert_exists ${repo_path}/${filename}
done

[ -e repo/dists/stable/main/debian-installer ] \
    && fail 'debian-installer directory should not be created'

# vim:set ai et sw=4 ts=4 tw=75:
