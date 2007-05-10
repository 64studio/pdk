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

# pdk repogen with dumpmeta comp should dump the metadata found in the
# component.

. atest/utils/repogen-fixture.sh

set_up_repogen_fixture test-repogen
cd test-repogen

pdk dumpmeta progeny.com/python.xml | diff -u /dev/null -

# rewrite component descriptor but with metadata.
cat >includemeta.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <meta>
    <other>value</other>
  </meta>
  <contents>
    <component>progeny.com/python.xml</component>
    <deb>
      <name>python</name>
      <meta>
        <key>value</key>
      </meta>
    </deb>
  </contents>
</component>
EOF

pdk dumpmeta includemeta.xml >metadump.txt

diff -u - metadump.txt <<EOF
md5:f390c2d3e8bc211a3d797b045c1ca4a0|deb|python|key|value
includemeta.xml|component||other|value
EOF

# vim:set ai et sw=4 ts=4 tw=75:
