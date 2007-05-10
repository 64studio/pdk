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

# The resolve command should catch odd filenames and note them in the
# component descriptor. These names should be used by repogen.

. atest/test_lib.sh
. atest/utils/test_channel.sh

# Set umask now in preparation for later permissions checking.
umask 002

pdk workspace create resolve
cd resolve

cat >etc/channels.xml <<EOF
<?xml version="1.0"?>
<channels>
  <default>
    <type>dir</type>
    <path>channel</path>
  </default>
</channels>
EOF

mkdir channel
cp \
    ${PACKAGES}/apache2-common_2.0.53-5_i386.deb \
    ${PACKAGES}/apache2_2.0.53-5.dsc \
    ${PACKAGES}/apache2_2.0.53-5.diff.gz \
    ${PACKAGES}/apache2_2.0.53.orig.tar.gz \
    ${PACKAGES}/adjtimex-1.13-12.i386.rpm \
    ${PACKAGES}/adjtimex-1.13-12.src.rpm \
    channel

# mess with some filenames
mv channel/apache2-common_2.0.53-5_i386.deb channel/a2c.deb
mv channel/apache2_2.0.53-5.dsc channel/a2.dsc
mv channel/adjtimex-1.13-12.i386.rpm channel/at.rpm
mv channel/adjtimex-1.13-12.src.rpm channel/at.src.rpm

pdk channel update

# ------------------------------------------------------------
# Test resolve and compile against odd filename debs
# ------------------------------------------------------------

cat >weird-apache.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <deb>apache2-common</deb>
  </contents>
</component>
EOF

pdk resolve weird-apache.xml

# include apache2-common to get an architecture for repogen
diff -u - weird-apache.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <deb>
      <name>apache2-common</name>
      <deb ref="md5:5acd04d4cc6e9d1530aad04accdc8eb5">
        <name>apache2-common</name>
        <version>2.0.53-5</version>
        <arch>i386</arch>
        <meta>
          <filename>a2c.deb</filename>
        </meta>
      </deb>
      <dsc ref="md5:d94c995bde2f13e04cdd0c21417a7ca5">
        <name>apache2</name>
        <version>2.0.53-5</version>
        <meta>
          <filename>a2.dsc</filename>
        </meta>
      </dsc>
    </deb>
  </contents>
</component>
EOF

pdk download weird-apache.xml
pdk repogen weird-apache.xml

no_exist="apache2_2.0.53-5.dsc apache2-common_2.0.53-5_i386.deb"
yes_exist="apache2_2.0.53-5.diff.gz apache2_2.0.53.orig.tar.gz"
yes_exist="$yes_exist a2c.deb a2.dsc"

for file in $no_exist; do
    fullname=repo/pool/main/a/apache2/$file
    [ -e $fullname ] && fail "$fullname should not exist"
done

for file in $yes_exist; do
    fullname=repo/pool/main/a/apache2/$file
    [ -e $fullname ] || fail "$fullname should exist"
done

grep a2.dsc repo/dists/weird-apache/main/source/Sources
grep a2c.deb repo/dists/weird-apache/main/binary-i386/Packages
grep apache2_2.0.53-5.dsc \
    repo/dists/weird-apache/main/source/Sources \
    && fail 'only the odd dsc should show up in Sources'
grep apache2-common_2.0.53-5_i386.deb \
    repo/dists/weird-apache/main/binary-i386/Packages \
    && fail 'only the odd deb should show up in Packages'

# ------------------------------------------------------------
# Test resolve and compile against odd filename rpms
# ------------------------------------------------------------

rm -r repo

cat >weird-adjtimex.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <rpm>adjtimex</rpm>
  </contents>
</component>
EOF

pdk resolve weird-adjtimex.xml

diff -u - weird-adjtimex.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <rpm>
      <name>adjtimex</name>
      <rpm ref="md5:b4f3deace0a3e92765555e7efa75ab59">
        <name>adjtimex</name>
        <version>1.13-12</version>
        <arch>i386</arch>
        <meta>
          <filename>at.rpm</filename>
        </meta>
      </rpm>
      <srpm ref="md5:3132a135dd01a5df9da9bc4ce94445a8">
        <name>adjtimex</name>
        <version>1.13-12</version>
        <meta>
          <filename>at.src.rpm</filename>
        </meta>
      </srpm>
    </rpm>
  </contents>
</component>
EOF

pdk download weird-adjtimex.xml
pdk repogen weird-adjtimex.xml

find repo

no_exist="adjtimex-1.13-12.i386.rpm adjtimex-1.13-12.src.rpm"
yes_exist="at.src.rpm at.rpm"

for file in $no_exist; do
    fullname=repo/$file
    [ -e $fullname ] && fail "$fullname should not exist"
done

for file in $yes_exist; do
    fullname=repo/$file
    [ -e $fullname ] || fail "$fullname should exist"
done

# vim:set ai et sw=4 ts=4 tw=75:
