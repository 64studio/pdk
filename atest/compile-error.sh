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

# Make sure that an error is raised if the user tries to put a package
# directly in a component marked with split-apt-components.

. atest/utils/repogen-fixture.sh

set_up_repogen_fixture test-repogen
cd test-repogen

# The deb reference is what triggers the error.

cat >product.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <id>product</id>
  <name>The Product</name>
  <requires>a</requires>
  <provides>b</provides>
  <meta>
    <apt-deb.id>product</apt-deb.id>
    <apt-deb.origin>community</apt-deb.origin>
    <apt-deb.label>distro</apt-deb.label>
    <apt-deb.version>1.0</apt-deb.version>
    <apt-deb.codename>zip</apt-deb.codename>
    <apt-deb.suite>stable</apt-deb.suite>
    <apt-deb.date>Tue, 22 Mar 2005 21:20:00 +0000</apt-deb.date>
    <apt-deb.description>Hello World!</apt-deb.description>
    <apt-deb.split-apt-components>yes</apt-deb.split-apt-components>
  </meta>
  <contents>
    <component>main.xml</component>
    <component>contrib.xml</component>
    <deb>
      <name>ida</name>
      <deb ref="sha-1:a5b9ebe5914fa4fa2583b1f5eb243ddd90e6fbbe">
        <name>ida</name>
        <version>2.01-1.2</version>
        <arch>arm</arch>
      </deb>
    </deb>
  </contents>
</component>
EOF

pdk repogen product.xml && fail 'repogen should have failed'

# vim:set ai et sw=4 ts=4 tw=75:
