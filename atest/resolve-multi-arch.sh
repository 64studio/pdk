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

# The resolve command should work when binaries from multiple architectures
# are spread across channels. When packages are duplicated between the
# channels, they should only show up once in the component descriptor.

. atest/utils/test_channel.sh

pdk workspace create resolve
cd resolve

# -----------------------------------------------------------
# Resolve from a pile of packages on the local filesystem.
# -----------------------------------------------------------

# Add some concrete and abstract package references to a new component.
cat >xsok.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <deb>xsok</deb>
  </contents>
</component>
EOF

make_channel x86 \
    xsok_1.02-9.dsc \
    xsok_1.02-9.diff.gz \
    xsok_1.02.orig.tar.gz \
    xsok_1.02-9_i386.deb

make_channel ia64 \
    xsok_1.02-9.dsc \
    xsok_1.02-9.diff.gz \
    xsok_1.02.orig.tar.gz \
    xsok_1.02-9_ia64.deb

cat >etc/channels.xml <<EOF
<?xml version="1.0"?>
<channels>
  <x86>
    <type>dir</type>
    <path>x86</path>
  </x86>
  <ia64>
    <type>dir</type>
    <path>ia64</path>
  </ia64>
</channels>
EOF

pdk channel update

pdk resolve xsok.xml

# Check that the result is what we expect
# Note, xml comments are not preseved.
diff -u - xsok.xml <<EOF || bail 'xsok.xml differs'
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <deb>
      <name>xsok</name>
      <deb ref="md5:42926c5789c4c684bf9844ab6a1afe0d">
        <name>xsok</name>
        <version>1.02-9</version>
        <arch>i386</arch>
      </deb>
      <deb ref="md5:bf98a669a087a57e9a05245440431b25">
        <name>xsok</name>
        <version>1.02-9</version>
        <arch>ia64</arch>
      </deb>
      <dsc ref="md5:c2a02a1c12dc59f8c410663cd38db12d">
        <name>xsok</name>
        <version>1.02-9</version>
      </dsc>
    </deb>
  </contents>
</component>
EOF

# vim:set ai et sw=4 ts=4 tw=75:
