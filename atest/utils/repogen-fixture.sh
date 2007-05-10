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

# This fixture creates a workspace with empty version control and a
# few component descriptors likely to be useful for testing repository
# generation code.

# By default the product descriptor specifies explicit apt-components
# and only debian packages.

. atest/test_lib.sh

set_up_repogen_fixture() {
    workspace_name="$1"

    pdk workspace create $workspace_name
    pushd $workspace_name

    cat >product.xml <<"EOF"
<?xml version="1.0"?>
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
  </contents>
</component>
EOF

    cat >contrib.xml <<"EOF"
<?xml version="1.0"?>
<component>
  <contents>
    <component>progeny.com/ida.xml</component>
  </contents>
</component>
EOF

    cat >main.xml <<"EOF"
<?xml version="1.0"?>
<component>
  <contents>
    <component>progeny.com/apache.xml</component>
  </contents>
</component>
EOF


    mkdir repogen-fixture-channel
    cp \
        ${PACKAGES}/apache2-common_2.0.53-5_i386.deb \
        ${PACKAGES}/apache2_2.0.53-5.dsc \
        ${PACKAGES}/apache2_2.0.53-5.diff.gz \
        ${PACKAGES}/apache2_2.0.53.orig.tar.gz \
        ${PACKAGES}/ida_2.01-1.2_arm.deb \
        ${PACKAGES}/ida_2.01-1.2.dsc \
        ${PACKAGES}/ida_2.01-1.2.diff.gz \
        ${PACKAGES}/ida_2.01.orig.tar.gz \
        ${PACKAGES}/emacs-defaults_1.1_all.deb \
        ${PACKAGES}/emacs-defaults_1.1.dsc \
        ${PACKAGES}/emacs-defaults_1.1.tar.gz \
        ${PACKAGES}/python-defaults_2.3.3-6.dsc \
        ${PACKAGES}/python-defaults_2.3.3-6.tar.gz \
        ${PACKAGES}/python_2.3.3-6_all.deb \
        ${PACKAGES}/adjtimex-1.13-13.i386.rpm \
        ${PACKAGES}/adjtimex-1.13-13.src.rpm \
        repogen-fixture-channel

    cat >etc/channels.xml <<EOF
<?xml version="1.0"?>
<channels>
  <repogen>
    <type>dir</type>
    <path>repogen-fixture-channel</path>
  </repogen>
</channels>
EOF

    pdk channel update

    mkdir progeny.com
    cat >progeny.com/apache.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <dsc>apache2</dsc>
  </contents>
</component>
EOF

    cat >progeny.com/ida.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <dsc>ida</dsc>
  </contents>
</component>
EOF

    cat >progeny.com/emacs.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <dsc>emacs-defaults</dsc>
  </contents>
</component>
EOF

    cat >progeny.com/python.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <dsc>python-defaults</dsc>
  </contents>
</component>
EOF

    cat >progeny.com/time.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <srpm>adjtimex</srpm>
  </contents>
</component>
EOF

    pdk resolve -R \
        progeny.com/apache.xml \
        progeny.com/ida.xml \
        progeny.com/emacs.xml \
        progeny.com/python.xml \
        progeny.com/time.xml

    popd
}

# vim:set ai et sw=4 ts=4 tw=75:
