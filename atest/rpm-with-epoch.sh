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

#  Will check that pdk works with RPMs that have and have not epochs.

pdk workspace create test
pushd test

mkdir channel-1

cp $tmp_dir/packages/centos-release-4-1.2.i386.rpm channel-1/
cp $tmp_dir/packages/passwd-0.68-10.i386.rpm channel-1/

cat >etc/channels.xml <<EOF
<?xml version="1.0"?>
<channels>
  <channel-1>
    <type>dir</type>
    <path>$tmp_dir/channel-1</path>
  </channel-1>
</channels>
EOF

cat >rpms.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <id>centos-test</id>
  <name>CentOS Test</name>
  <contents>
    <rpm>centos-release</rpm>
    <rpm>passwd</rpm>
  </contents>
</component>
EOF

pdk channel update

# vim:set ai et sw=4 ts=4 tw=75:
