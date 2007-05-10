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

# pdk can handle udebs.

pdk workspace create test-with-dir-channel
pushd test-with-dir-channel
    cat >etc/channels.xml <<EOF
<?xml version="1.0"?>
<channels>
  <ddetect>
    <type>dir</type>
    <path>ddetect-pkg</path>
  </ddetect>
</channels>
EOF

    mkdir ddetect-pkg
    cp $PACKAGES/ddetect/* ddetect-pkg

    pdk channel update

    cat >ddetect.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <dsc>ddetect</dsc>
  </contents>
</component>
EOF

    cat >meta-overrides.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <udeb>
      <name>ethdetect</name>
      <meta>
        <deb.installer-menu-item>12</deb.installer-menu-item>
        <comment>Move menu item</comment>
      </meta>
    </udeb>
    <udeb>
      <name>hw-detect-full</name>
      <meta>
        <deb.Priority>optional</deb.Priority>
        <zippy>test test test</zippy>
      </meta>
    </udeb>
  </contents>
</component>
EOF

    cat >product.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <component>ddetect.xml</component>
    <component>meta-overrides.xml</component>
  </contents>
</component>
EOF

    pdk resolve -R ddetect.xml

    pdk download ddetect.xml
    pdk repogen product.xml

    sources=repo/dists/product/main/source/Sources
    diff -u - $sources <<EOF
Package: ddetect
Binary: archdetect, ethdetect, hw-detect-full, hw-detect
Version: 1.14
Maintainer: Debian Install System Team <debian-boot@lists.debian.org>
Build-Depends: debhelper (>= 4.2), dpkg-dev (>= 1.9.0), po-debconf (>= 0.5.0), libdebconfclient0-dev
Architecture: any
Standards-Version: 3.6.1.0
Format: 1.0
Directory: pool/main/d/ddetect
Files:
 495af96bbce91412391763a053efda2c 874 ddetect_1.14.dsc
 c7d7453fbbbf7d653e39e1d4e5e4f874 104863 ddetect_1.14.tar.gz
Uploaders: Petter Reinholdtsen <pere@debian.org>, Joey Hess <joeyh@debian.org>, Joshua Kwan <joshk@triplehelix.org>, Matt Kraai <kraai@debian.org>, Christian Perrier <bubulle@debian.org>, Colin Watson <cjwatson@debian.org>, Bdale Garbee <bdale@gag.com>

EOF

    packages=repo/dists/product/main/debian-installer/binary-i386/Packages
    diff -u - $packages <<EOF
Package: archdetect
Priority: standard
Section: debian-installer
Installed-Size: 20
Maintainer: Debian Install System Team <debian-boot@lists.debian.org>
Architecture: i386
Source: ddetect
Version: 1.14
Filename: pool/main/d/ddetect/archdetect_1.14_i386.udeb
Size: 2350
MD5Sum: b975d0ea66a5fc55a5eacb24701da3ea
Description: Hardware architecture detector

Package: ethdetect
Priority: optional
Section: debian-installer
Installed-Size: 104
Maintainer: Debian Install System Team <debian-boot@lists.debian.org>
Architecture: all
Source: ddetect
Version: 1.14
Provides: ethernet-card-detection
Depends: cdebconf-udeb (>= 0.38), hw-detect
Filename: pool/main/d/ddetect/ethdetect_1.14_all.udeb
Size: 30616
MD5Sum: 498d5ab10fc12f87d303da9f60c2f045
Description: Detect network hardware and load kernel drivers for it
installer-menu-item: 12

Package: hw-detect
Priority: standard
Section: debian-installer
Installed-Size: 160
Maintainer: Debian Install System Team <debian-boot@lists.debian.org>
Architecture: i386
Source: ddetect
Version: 1.14
Depends: discover, rootskel (>= 0.54), archdetect
Filename: pool/main/d/ddetect/hw-detect_1.14_i386.udeb
Size: 50732
MD5Sum: 78c1432319d541717eee0b6720231caf
Description: Detect hardware and load kernel drivers for it

Package: hw-detect-full
Priority: optional
Section: debian-installer
Installed-Size: 20
Maintainer: Debian Install System Team <debian-boot@lists.debian.org>
Architecture: all
Source: ddetect
Version: 1.14
Provides: harddrive-detection
Depends: cdebconf-udeb (>= 0.38), hw-detect
Filename: pool/main/d/ddetect/hw-detect-full_1.14_all.udeb
Size: 2676
MD5Sum: 5f371e52fca4376003fc7ff6b729d0df
Description: Detect hardware and load kernel drivers for it (full version)
Enhances: hw-detect
installer-menu-item: 35

EOF

popd

# vim:set ai et sw=4 ts=4 tw=75:
