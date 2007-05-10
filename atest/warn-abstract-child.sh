# $Progeny$
#
#   Copyright 2006 Progeny Linux Systems, Inc.
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

# resolve should warn the user if unresolved references remain.

. atest/test_lib.sh

mkdir channel
cp ${PACKAGES}/apache2*_2.0.53* channel

pdk workspace create workspace

cd workspace
# notice that the first child of the abstract reference is also abstract.
cat >perl.xml <<EOF
<?xml version="1.0" encoding="utf-8"?>
<component>
  <contents>
    <deb>
      <name>perl</name>
      <deb>
        <name>perl</name>
        <version>5.8.4-8sarge3</version>
        <arch>amd64</arch>
      </deb>
    </deb>
  </contents>
</component>
EOF

cp perl.xml perl2.xml

pdk channel update
set -x
pdk semdiff perl.xml perl2.xml 2>error \
    || { status=$?; cat error; exit $status; }
grep "^pdk WARNING: Child reference is abstract" error

# vim:set ai et sw=4 ts=4 tw=75:
