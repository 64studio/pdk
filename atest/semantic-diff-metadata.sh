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

# Semantic diff should detect changes in component metadata.

. atest/test_lib.sh

pdk workspace create work
cd work

cat >etc/channels.xml <<EOF
<?xml version="1.0"?>
<channels>
  <local>
    <type>dir</type>
    <path>channel</path>
  </local>
</channels>
EOF

mkdir channel
cp $tmp_dir/packages/ethereal_0.9.4-1woody2_i386.deb channel

cat >ethereal.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <component>meta-info.xml</component>
    <deb>ethereal</deb>
  </contents>
</component>
EOF

cat >meta-info.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <deb>
      <name>ethereal</name>
      <version>0.9.4-1woody2</version>
      <meta>
        <predicate>test-stage-1</predicate>
      </meta>
    </deb>
  </contents>
</component>
EOF

pdk channel update
pdk resolve ethereal.xml
pdk download ethereal.xml

pdk add ethereal.xml
pdk add meta-info.xml
pdk commit -m 'Starting point for diff.'

# Nothing should have changed yet.
pdk semdiff --show-unchanged -m ethereal.xml | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
unchanged|deb|ethereal|0.9.4-1woody2|0.9.4-1woody2|i386|ethereal.xml
EOF

rm -r channel
mkdir channel
cp $tmp_dir/packages/ethereal_0.9.4-1woody3_i386.deb channel

cat >ethereal.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <component>meta-info.xml</component>
    <deb>ethereal</deb>
  </contents>
</component>
EOF

pdk channel update
pdk resolve ethereal.xml
pdk download ethereal.xml

pdk semdiff --show-unchanged -m ethereal.xml | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
meta-drop|deb|ethereal|i386|predicate|test-stage-1
upgrade|deb|ethereal|0.9.4-1woody2|0.9.4-1woody3|i386|ethereal.xml
EOF

pdk commit -m 'Commit changes.'

rm -r channel
mkdir channel
cp $tmp_dir/packages/ethereal_0.9.4-1woody2_i386.deb channel

cat >ethereal.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <component>meta-info.xml</component>
    <deb>ethereal</deb>
  </contents>
</component>
EOF

pdk channel update
pdk resolve ethereal.xml
pdk download ethereal.xml

pdk semdiff --show-unchanged -m ethereal.xml | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
downgrade|deb|ethereal|0.9.4-1woody3|0.9.4-1woody2|i386|ethereal.xml
meta-add|deb|ethereal|i386|predicate|test-stage-1
EOF

# vim:set ai et sw=4 ts=4 tw=75:
