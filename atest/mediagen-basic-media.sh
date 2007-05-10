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

# Create simple media from a component descriptor.

. atest/utils/repogen-fixture.sh

set_up_repogen_fixture test-mediagen
cd test-mediagen

cat >distro.xml <<EOF
<?xml version="1.0"?>
<component>
  <meta>
    <mediagen.media>cd</mediagen.media>
    <mediagen.repository>distro:main</mediagen.repository>
    <mediagen.source>immediate</mediagen.source>
    <mediagen.no-debootstrap>true</mediagen.no-debootstrap>
  </meta>
  <contents>
    <component>progeny.com/apache.xml</component>
  </contents>
</component>
EOF

pdk repogen distro.xml
pdk mediagen distro.xml

isoinfo -i images/img-bin1.iso -fJ | LANG=C sort >iso-list.txt

diff -u - iso-list.txt <<EOF
/TRANS.TBL
/dists
/dists/TRANS.TBL
/dists/distro
/dists/distro/Release
/dists/distro/TRANS.TBL
/dists/distro/main
/dists/distro/main/TRANS.TBL
/dists/distro/main/binary-i386
/dists/distro/main/binary-i386/Packages
/dists/distro/main/binary-i386/Packages.gz
/dists/distro/main/binary-i386/Release
/dists/distro/main/binary-i386/TRANS.TBL
/dists/distro/main/source
/dists/distro/main/source/Release
/dists/distro/main/source/Sources
/dists/distro/main/source/Sources.gz
/dists/distro/main/source/TRANS.TBL
/pool
/pool/TRANS.TBL
/pool/main
/pool/main/TRANS.TBL
/pool/main/a
/pool/main/a/TRANS.TBL
/pool/main/a/apache2
/pool/main/a/apache2/TRANS.TBL
/pool/main/a/apache2/apache2-common_2.0.53-5_i386.deb
/pool/main/a/apache2/apache2_2.0.53-5.diff.gz
/pool/main/a/apache2/apache2_2.0.53-5.dsc
/pool/main/a/apache2/apache2_2.0.53.orig.tar.gz
EOF

# vim:set ai et sw=4 ts=4 tw=75:
