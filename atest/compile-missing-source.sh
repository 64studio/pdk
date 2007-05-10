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

# Watch for regression. prc bombed when a binary was presented without it's
# source.

. atest/utils/repogen-fixture.sh

set_up_repogen_fixture test-repogen
cd test-repogen

# this component is missing a source package.
cat >progeny.com/apache.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <dsc>
      <name>apache2</name>
      <deb ref="md5:5acd04d4cc6e9d1530aad04accdc8eb5">
        <name>apache2-common</name>
        <version>2.0.53-5</version>
        <arch>i386</arch>
      </deb>
    </dsc>
  </contents>
</component>
EOF

pdk repogen progeny.com/apache.xml

[ -d './repo' ] || fail "mising repo directory"

check_file "b7d31cf9a160c3aadaf5f1cd86cdc8762b3d4b1b" \
    "./repo/pool/main/a/apache2/apache2-common_2.0.53-5_i386.deb"

assert_exists repo/dists/apache/main/binary-i386/Packages.gz
assert_not_exists repo/dists/apache/main/source/Sources.gz

assert_exists repo/dists/apache/Release
assert_exists repo/dists/apache/main/binary-i386/Release
assert_not_exists repo/dists/apache/main/source/Release

grep apache repo/dists/apache/main/binary-i386/Packages

# vim:set ai et sw=4 ts=4 tw=75:
