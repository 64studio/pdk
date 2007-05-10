# $Progeny$
#
#   Copyright 2005, 2006 Progeny Linux Systems, Inc.
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

# Check that we can import and then do a basic compile using RPMs.

. atest/utils/repogen-fixture.sh

set_up_repogen_fixture test-repogen
cd test-repogen

# this component mentions the same rpm twice, to catch a regression.
cat >time.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <srpm>
      <name>adjtimex</name>
      <rpm ref="md5:2c0376dce66844970269876d1e09fea9">
        <name>adjtimex</name>
        <version>1.13-13</version>
        <arch>i386</arch>
      </rpm>
      <rpm ref="md5:2c0376dce66844970269876d1e09fea9">
        <name>adjtimex</name>
        <version>1.13-13</version>
        <arch>i386</arch>
      </rpm>
      <srpm ref="md5:adf064bd5d34ee4522a01fd15176d9b6">
        <name>adjtimex</name>
        <version>1.13-13</version>
      </srpm>
    </srpm>
  </contents>
</component>
EOF

pdk repogen time.xml

[ -d './repo' ] || fail "mising repo directory"

check_file "519da15c87652669b707ab49e2a6294d7aea1c1f" \
    "./repo/adjtimex-1.13-13.i386.rpm"
check_file "5f5e2555c8294e68d06bf61aad10daa05dca2516" \
    "./repo/adjtimex-1.13-13.src.rpm"

# vim:set ai et sw=4 ts=4 tw=75:
