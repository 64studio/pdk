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

# Watch for regression where running repogen twice causes a stack trace.

. atest/test_lib.sh

#Setup
#create a local package "channel" and
#populate it with package files
mkdir channel
cp packages/apache2*_2.0.53* channel

#Create a workspace.  Always.
pdk workspace create doublecompile
cd doublecompile

#create the channel configuration file
cat >etc/channels.xml <<EOF
<?xml version="1.0"?>
<channels>
  <local>
    <type>dir</type>
    <path>../channel</path>
  </local>
</channels>
EOF

#instruct pdk to populate the local cache
#from the configured channel
pdk channel update

#make a component
cat >apache.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <dsc ref="md5:d94c995bde2f13e04cdd0c21417a7ca5">
      <name>apache2</name>
      <version>2.0.53-5</version>
    </dsc>
    <deb ref="md5:5acd04d4cc6e9d1530aad04accdc8eb5">
      <name>apache2-common</name>
      <version>2.0.53-5</version>
      <arch>i386</arch>
    </deb>
  </contents>
</component>
EOF

#Acquire the package files for the component
pdk download apache.xml

pdk repogen apache.xml
pdk repogen apache.xml

# vim:set ai et sw=4 ts=4 tw=75:
