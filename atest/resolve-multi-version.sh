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

# When more than one package matches a reference, use the most up to date
# version. Also watch for a regression when two multi-version resolves show
# up in the same component.

pdk workspace create multi-version
pushd multi-version
    mkdir channel
    cp \
        $PACKAGES/ethereal-dev_0.9.4-1woody5_i386.deb \
        $PACKAGES/ethereal-dev_0.9.4-1woody5_ia64.deb \
        $PACKAGES/ethereal-dev_0.9.4-1woody6_i386.deb \
        $PACKAGES/ethereal-dev_0.9.4-1woody6_ia64.deb \
        $PACKAGES/ethereal-common_0.9.4-1woody5_i386.deb \
        $PACKAGES/ethereal-common_0.9.4-1woody5_ia64.deb \
        $PACKAGES/ethereal-common_0.9.4-1woody6_i386.deb \
        $PACKAGES/ethereal-common_0.9.4-1woody6_ia64.deb \
        $PACKAGES/ethereal_0.9.4-1woody5.dsc \
        $PACKAGES/ethereal_0.9.4-1woody5.diff.gz \
        $PACKAGES/ethereal_0.9.4-1woody5_i386.deb \
        $PACKAGES/ethereal_0.9.4-1woody5_ia64.deb \
        $PACKAGES/ethereal_0.9.4-1woody6.diff.gz \
        $PACKAGES/ethereal_0.9.4-1woody6.dsc \
        $PACKAGES/ethereal_0.9.4-1woody6_i386.deb \
        $PACKAGES/ethereal_0.9.4-1woody6_ia64.deb \
        $PACKAGES/ethereal_0.9.4.orig.tar.gz \
        $PACKAGES/tethereal_0.9.4-1woody5_i386.deb \
        $PACKAGES/tethereal_0.9.4-1woody5_ia64.deb \
        $PACKAGES/tethereal_0.9.4-1woody6_i386.deb \
        $PACKAGES/tethereal_0.9.4-1woody6_ia64.deb \
        $PACKAGES/mount_2.12p-4_amd64.deb \
        $PACKAGES/util-linux_2.12p-4_amd64.deb \
        $PACKAGES/util-linux_2.12p-4.diff.gz \
        $PACKAGES/util-linux_2.12p-4.dsc \
        $PACKAGES/mount_2.12p-4sarge1_amd64.deb \
        $PACKAGES/util-linux_2.12p-4sarge1_amd64.deb \
        $PACKAGES/util-linux_2.12p-4sarge1.diff.gz \
        $PACKAGES/util-linux_2.12p-4sarge1.dsc \
        $PACKAGES/util-linux_2.12p.orig.tar.gz \
        channel

    cat >etc/channels.xml <<EOF
<?xml version="1.0"?>
<channels>
  <local>
    <type>dir</type>
    <path>channel</path>
  </local>
</channels>
EOF

    pdk channel update

    cat >ethereal.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <dsc>ethereal</dsc>
    <deb>ethereal</deb>
    <deb>tethereal</deb>
    <deb>mount</deb>
    <deb>util-linux</deb>
  </contents>
</component>
EOF

    pdk resolve ethereal.xml
    diff -u - ethereal.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <dsc>
      <name>ethereal</name>
      <deb ref="md5:b9efde468cca1ddd6b731a3b343bd51d">
        <name>ethereal</name>
        <version>0.9.4-1woody6</version>
        <arch>i386</arch>
      </deb>
      <deb ref="md5:e2aba915304534ac4fbb060a2552d9c6">
        <name>ethereal</name>
        <version>0.9.4-1woody6</version>
        <arch>ia64</arch>
      </deb>
      <deb ref="md5:c618774e3718d11d94347b0d66f72af4">
        <name>ethereal-common</name>
        <version>0.9.4-1woody6</version>
        <arch>i386</arch>
      </deb>
      <deb ref="md5:f06169aeefd918e4e5b809393edb8dc2">
        <name>ethereal-common</name>
        <version>0.9.4-1woody6</version>
        <arch>ia64</arch>
      </deb>
      <deb ref="md5:a7c01d2560880e783e899cd623a27e7a">
        <name>ethereal-dev</name>
        <version>0.9.4-1woody6</version>
        <arch>i386</arch>
      </deb>
      <deb ref="md5:e7f788d020319a8147beb4172cdc736f">
        <name>ethereal-dev</name>
        <version>0.9.4-1woody6</version>
        <arch>ia64</arch>
      </deb>
      <deb ref="md5:a7706f7f82b44a30d4a99b299c58b4ca">
        <name>tethereal</name>
        <version>0.9.4-1woody6</version>
        <arch>i386</arch>
      </deb>
      <deb ref="md5:6c8ef685b4e61f34a0146eb6fc666fdb">
        <name>tethereal</name>
        <version>0.9.4-1woody6</version>
        <arch>ia64</arch>
      </deb>
      <dsc ref="md5:6c3d2beab693578b827bc0c2ecc13eb2">
        <name>ethereal</name>
        <version>0.9.4-1woody6</version>
      </dsc>
    </dsc>
    <deb>
      <name>ethereal</name>
      <deb ref="md5:b9efde468cca1ddd6b731a3b343bd51d">
        <name>ethereal</name>
        <version>0.9.4-1woody6</version>
        <arch>i386</arch>
      </deb>
      <deb ref="md5:e2aba915304534ac4fbb060a2552d9c6">
        <name>ethereal</name>
        <version>0.9.4-1woody6</version>
        <arch>ia64</arch>
      </deb>
      <dsc ref="md5:6c3d2beab693578b827bc0c2ecc13eb2">
        <name>ethereal</name>
        <version>0.9.4-1woody6</version>
      </dsc>
    </deb>
    <deb>
      <name>tethereal</name>
      <deb ref="md5:a7706f7f82b44a30d4a99b299c58b4ca">
        <name>tethereal</name>
        <version>0.9.4-1woody6</version>
        <arch>i386</arch>
      </deb>
      <deb ref="md5:6c8ef685b4e61f34a0146eb6fc666fdb">
        <name>tethereal</name>
        <version>0.9.4-1woody6</version>
        <arch>ia64</arch>
      </deb>
      <dsc ref="md5:6c3d2beab693578b827bc0c2ecc13eb2">
        <name>ethereal</name>
        <version>0.9.4-1woody6</version>
      </dsc>
    </deb>
    <deb>
      <name>mount</name>
      <deb ref="md5:b8f5b355beb87bc3637861fc526c6d85">
        <name>mount</name>
        <version>2.12p-4sarge1</version>
        <arch>amd64</arch>
      </deb>
      <dsc ref="md5:9341316ba59e695a6bc89cd9ecda5f65">
        <name>util-linux</name>
        <version>2.12p-4sarge1</version>
      </dsc>
    </deb>
    <deb>
      <name>util-linux</name>
      <deb ref="md5:361df6632f69bac77bf290f5ab9a0f71">
        <name>util-linux</name>
        <version>2.12p-4sarge1</version>
        <arch>amd64</arch>
      </deb>
      <dsc ref="md5:9341316ba59e695a6bc89cd9ecda5f65">
        <name>util-linux</name>
        <version>2.12p-4sarge1</version>
      </dsc>
    </deb>
  </contents>
</component>
EOF
popd

# vim:set ai et sw=4 ts=4 tw=75:
