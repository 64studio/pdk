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

# Catch regression of problem where resolving with two channels could result
# in a type constraint being ignored.
. atest/test_lib.sh

# Setup channels
mkdir channel-1
dir_channel1=$(pwd)/channel-1
cp atest/packages/xsok_1.02-9woody2.dsc channel-1/
cp atest/packages/xsok_1.02-9woody2.diff.gz channel-1/
cp atest/packages/xsok_1.02.orig.tar.gz channel-1/

mkdir channel-2
dir_channel2=$(pwd)/channel-1
cp atest/packages/xsok_1.02-9woody2_i386.deb channel-2

# Create workspace
pdk workspace create workspace

# Add channels file to workspace root
cd workspace
cat >etc/channels.xml <<EOF
<?xml version="1.0"?>
<channels>
  <channel-1>
    <type>dir</type>
    <path>${dir_channel1}</path>
  </channel-1>
  <channel-2>
    <type>dir</type>
    <path>${dir_channel2}</path>
  </channel-2>
</channels>
EOF

cat >xsok.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <dsc>xsok</dsc>
  </contents>
</component>
EOF

pdk channel update
pdk resolve xsok.xml -c channel-1 -c channel-2

cat >expected <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <dsc>
      <name>xsok</name>
      <dsc ref="md5:5e3f7f8513b7fb3e8fa1ebfa56a2b4bc">
        <name>xsok</name>
        <version>1.02-9woody2</version>
      </dsc>
    </dsc>
  </contents>
</component>
EOF

diff -u expected xsok.xml  || bail "did not resolve as expected"

# vim:set ai et sw=4 ts=4 tw=75:
