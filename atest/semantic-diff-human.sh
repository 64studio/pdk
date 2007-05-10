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

# Test pdk semdiff human readable format.
# We aren't really testing the content of the report, just that it is
# generated quietly. Actual semantics are tested elsewhere.

assert_empty() {
    empty_file="$1"
    if [ "$(stat -c '%s' $empty_file)" != 0 ]; then
        cat "$empty_file"
        fail "$empty_file should be empty"
    fi
}

semdiff_report () {
    pdk semdiff "$@" 2>errors.txt | ul
    assert_empty errors.txt
    rm errors.txt
}

. atest/utils/semdiff-fixture.sh

set_up_semdiff_fixture test-semdiff
cd test-semdiff

cp ethereal1.xml ethereal.xml

cat >product.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <component>meta-info.xml</component>
    <compoennt>ethereal</component>
  </contents>
</component>
EOF

cat >meta-info.xml <<EOF
<?xml version="1.0"?>
<component>
  <contents>
    <deb>
      <name>ethereal</name>
      <version>0.9.4-1woody2</version>
      <meta>
        <predicate>test-stage-1</predicate>
      </meta>
    </deb>
  </contents>
</component>
EOF

pdk add ethereal.xml
pdk add meta-info.xml
pdk add product.xml

pdk commit -m 'Starting point for diff.'

semdiff_report ethereal.xml

cp ethereal2.xml ethereal.xml

semdiff_report ethereal.xml

pdk commit -m 'Commit changes.'

cp ethereal1.xml ethereal.xml

semdiff_report ethereal.xml

# Now check comparing two files.

semdiff_report timex-12.xml timex-12.xml

semdiff_report timex-12.xml timex-13.xml

semdiff_report timex-13.xml timex-12.xml

semdiff_report timex-12.xml timex-12-nosrc.xml

semdiff_report timex-12-nosrc.xml timex-12.xml

# vim:set ai et sw=4 ts=4 tw=75:
