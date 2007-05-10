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

# This fixture creates a workspace with empty version control and 6
# component desctiptors. Three descriptors contain rpms, three contain
# debs. The three descriptors contain packages which are older, newer,
# and older but with one package missing. This is designed for
# effective testing of semdiff.

set_up_semdiff_fixture() {

workspace_name="$1"

pdk workspace create $workspace_name
pushd $workspace_name

mkdir timex-channel
cp \
    ${PACKAGES}/adjtimex-1.13-12.i386.rpm \
    ${PACKAGES}/adjtimex-1.13-12.src.rpm \
    ${PACKAGES}/adjtimex-1.13-13.i386.rpm \
    ${PACKAGES}/adjtimex-1.13-13.src.rpm \
    timex-channel

mkdir ethereal-channel
cp \
    ${PACKAGES}/ethereal_0.9.13-1.0progeny1.dsc \
    ${PACKAGES}/ethereal_0.9.13-1.0progeny1.diff.gz \
    ${PACKAGES}/ethereal_0.9.13.orig.tar.gz \
    ${PACKAGES}/ethereal_0.9.13-1.0progeny1_ia64.deb \
    ${PACKAGES}/ethereal-common_0.9.13-1.0progeny1_ia64.deb \
    ${PACKAGES}/ethereal-dev_0.9.13-1.0progeny1_ia64.deb \
    ${PACKAGES}/tethereal_0.9.13-1.0progeny1_ia64.deb \
    ${PACKAGES}/ethereal_0.9.13-1.0progeny2.dsc \
    ${PACKAGES}/ethereal_0.9.13-1.0progeny2.diff.gz \
    ${PACKAGES}/ethereal_0.9.13-1.0progeny2_ia64.deb \
    ${PACKAGES}/ethereal-common_0.9.13-1.0progeny2_ia64.deb \
    ${PACKAGES}/ethereal-dev_0.9.13-1.0progeny2_ia64.deb \
    ${PACKAGES}/tethereal_0.9.13-1.0progeny2_ia64.deb \
    ethereal-channel

cat >etc/channels.xml <<EOF
<?xml version="1.0"?>
<channels>
  <timex>
    <type>dir</type>
    <path>timex-channel</path>
  </timex>
  <ethereal>
    <type>dir</type>
    <path>ethereal-channel</path>
  </ethereal>
</channels>
EOF

pdk channel update

# Some rpm descriptors containing various configurations.

cat >timex-12.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <rpm>
      <name>adjtimex</name>
      <srpm ref="md5:3132a135dd01a5df9da9bc4ce94445a8">
        <name>adjtimex</name>
        <version>1.13-12</version>
        <arch>x86_64</arch>
      </srpm>
      <rpm ref="md5:b4f3deace0a3e92765555e7efa75ab59">
        <name>adjtimex</name>
        <version>-1.13-12</version>
        <arch>i386</arch>
      </rpm>
    </rpm>
  </contents>
</component>
EOF

cat >timex-12-nosrc.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <rpm>
      <name>adjtimex</name>
      <rpm ref="md5:b4f3deace0a3e92765555e7efa75ab59">
        <name>adjtimex</name>
        <version>1.13-12</version>
        <arch>i386</arch>
      </rpm>
    </rpm>
  </contents>
</component>
EOF

cat >timex-13.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <rpm>
      <name>adjtimex</name>
      <srpm ref="md5:adf064bd5d34ee4522a01fd15176d9b6">
        <name>adjtimex</name>
        <version>1.13-13</version>
        <arch>x86_64</arch>
      </srpm>
      <rpm ref="md5:2c0376dce66844970269876d1e09fea9">
        <name>adjtimex</name>
        <version>1.13-13</version>
        <arch>i386</arch>
      </rpm>
    </rpm>
  </contents>
</component>
EOF

cat >ethereal1.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <dsc>
    <name>ethereal</name>
      <dsc ref="md5:5defb080766305d80e1b6c6e89d8c9e1">
        <name>ethereal</name>
        <version>0.9.13-1.0progeny1</version>
      </dsc>
      <deb ref="md5:e2faf101eba43cb4de0e4c9c13c7e2b6">
        <name>ethereal</name>
        <version>0.9.13-1.0progeny1</version>
        <arch>ia64</arch>
      </deb>
      <deb ref="md5:6295ec8bfbe7993f3003a0322ebf723e">
        <name>ethereal-common</name>
        <version>0.9.13-1.0progeny1</version>
        <arch>ia64</arch>
      </deb>
      <deb ref="md5:7f5a380122c1dbee501fa0744fe33a7a">
        <name>ethereal-dev</name>
        <version>0.9.13-1.0progeny1</version>
        <arch>ia64</arch>
      </deb>
      <deb ref="md5:56ff2d340f4121ceff0454dca254e646">
        <name>tethereal</name>
        <version>0.9.13-1.0progeny1</version>
        <arch>ia64</arch>
      </deb>
    </dsc>
  </contents>
</component>
EOF

cat >ethereal1-missing.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <dsc>
    <name>ethereal</name>
      <dsc ref="md5:5defb080766305d80e1b6c6e89d8c9e1">
        <name>ethereal</name>
        <version>0.9.13-1.0progeny1</version>
      </dsc>
      <deb ref="md5:6295ec8bfbe7993f3003a0322ebf723e">
        <name>ethereal-common</name>
        <version>0.9.13-1.0progeny1</version>
        <arch>ia64</arch>
      </deb>
      <deb ref="md5:7f5a380122c1dbee501fa0744fe33a7a">
        <name>ethereal-dev</name>
        <version>0.9.13-1.0progeny1</version>
        <arch>ia64</arch>
      </deb>
      <deb ref="md5:56ff2d340f4121ceff0454dca254e646">
        <name>tethereal</name>
        <version>0.9.13-1.0progeny1</version>
        <arch>ia64</arch>
      </deb>
    </dsc>
  </contents>
</component>
EOF

cat >ethereal2.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <dsc>
      <dsc ref="md5:c14c96a4046f4fdaee13d915db38f882">
        <name>ethereal</name>
        <version>0.9.13-1.0progeny2</version>
      </dsc>
      <deb ref="md5:495db2b093364a55c5954eb6b89a13df">
        <name>ethereal</name>
        <version>0.9.13-1.0progeny2</version>
        <arch>ia64</arch>
      </deb>
      <deb ref="md5:48c9b3d4b22b22e72ac5a992054e31ff">
        <name>ethereal-common</name>
        <version>0.9.13-1.0progeny2</version>
        <arch>ia64</arch>
      </deb>
      <deb ref="md5:fe1b75646c8fd7e769b4f16958efe75a">
        <name>ethereal-dev</name>
        <version>0.9.13-1.0progeny2</version>
        <arch>ia64</arch>
      </deb>
      <deb ref="md5:18bede30ec19d03770440903b157d16d">
        <name>tethereal</name>
        <version>0.9.13-1.0progeny2</version>
        <arch>ia64</arch>
      </deb>
    </dsc>
  </contents>
</component>
EOF

popd

}

# vim:set ai et sw=4 ts=4 tw=75:
