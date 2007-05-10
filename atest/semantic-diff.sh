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

# Test pdk semdiff

. atest/utils/semdiff-fixture.sh

set_up_semdiff_fixture test-semdiff
cd test-semdiff

# --------------------------------
# Test semdiff with rpms.
# --------------------------------

cp timex-12.xml time.xml
pdk add time.xml
pdk commit -m 'message'

pdk semdiff --show-unchanged -m time.xml | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
unchanged|rpm|adjtimex|1.13-12|1.13-12|i386|time.xml
unchanged|srpm|adjtimex|1.13-12|1.13-12|x86_64|time.xml
EOF

cp timex-13.xml time.xml
pdk semdiff --show-unchanged -m time.xml | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
upgrade|rpm|adjtimex|1.13-12|1.13-13|i386|time.xml
upgrade|srpm|adjtimex|1.13-12|1.13-13|x86_64|time.xml
EOF

pdk commit -m 'message'

cp timex-12.xml time.xml
pdk semdiff --show-unchanged -m time.xml | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
downgrade|rpm|adjtimex|1.13-13|1.13-12|i386|time.xml
downgrade|srpm|adjtimex|1.13-13|1.13-12|x86_64|time.xml
EOF

pdk commit -m 'message'

cp timex-12-nosrc.xml time.xml
pdk semdiff --show-unchanged -m time.xml | grep -v ^unchanged \
    | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
drop|srpm|adjtimex|1.13-12|x86_64|time.xml
EOF

pdk commit -m 'message'

cp timex-12.xml time.xml
pdk semdiff --show-unchanged -m time.xml | grep -v ^unchanged \
    | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
add|srpm|adjtimex|1.13-12|x86_64|time.xml
EOF

pdk commit -m 'message'

# --------------------------------
# Test semdiff with debs.
# --------------------------------

cp ethereal1.xml ethereal.xml
pdk add ethereal.xml
pdk commit -m 'message'

pdk semdiff --show-unchanged -m ethereal.xml | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
unchanged|deb|ethereal-common|0.9.13-1.0progeny1|0.9.13-1.0progeny1|ia64|ethereal.xml
unchanged|deb|ethereal-dev|0.9.13-1.0progeny1|0.9.13-1.0progeny1|ia64|ethereal.xml
unchanged|deb|ethereal|0.9.13-1.0progeny1|0.9.13-1.0progeny1|ia64|ethereal.xml
unchanged|deb|tethereal|0.9.13-1.0progeny1|0.9.13-1.0progeny1|ia64|ethereal.xml
unchanged|dsc|ethereal|0.9.13-1.0progeny1|0.9.13-1.0progeny1|any|ethereal.xml
EOF

cp ethereal2.xml ethereal.xml
pdk semdiff --show-unchanged -m ethereal.xml | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
upgrade|deb|ethereal-common|0.9.13-1.0progeny1|0.9.13-1.0progeny2|ia64|ethereal.xml
upgrade|deb|ethereal-dev|0.9.13-1.0progeny1|0.9.13-1.0progeny2|ia64|ethereal.xml
upgrade|deb|ethereal|0.9.13-1.0progeny1|0.9.13-1.0progeny2|ia64|ethereal.xml
upgrade|deb|tethereal|0.9.13-1.0progeny1|0.9.13-1.0progeny2|ia64|ethereal.xml
upgrade|dsc|ethereal|0.9.13-1.0progeny1|0.9.13-1.0progeny2|any|ethereal.xml
EOF

pdk commit -m 'message'

cp ethereal1.xml ethereal.xml
pdk semdiff --show-unchanged -m ethereal.xml | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
downgrade|deb|ethereal-common|0.9.13-1.0progeny2|0.9.13-1.0progeny1|ia64|ethereal.xml
downgrade|deb|ethereal-dev|0.9.13-1.0progeny2|0.9.13-1.0progeny1|ia64|ethereal.xml
downgrade|deb|ethereal|0.9.13-1.0progeny2|0.9.13-1.0progeny1|ia64|ethereal.xml
downgrade|deb|tethereal|0.9.13-1.0progeny2|0.9.13-1.0progeny1|ia64|ethereal.xml
downgrade|dsc|ethereal|0.9.13-1.0progeny2|0.9.13-1.0progeny1|any|ethereal.xml
EOF

pdk commit -m 'message'

cp ethereal1-missing.xml ethereal.xml
pdk semdiff --show-unchanged -m ethereal.xml | grep -v ^unchanged \
    | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
drop|deb|ethereal|0.9.13-1.0progeny1|ia64|ethereal.xml
EOF

pdk commit -m 'message'

cp ethereal1.xml ethereal.xml
pdk semdiff --show-unchanged -m ethereal.xml | grep -v ^unchanged \
    | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
add|deb|ethereal|0.9.13-1.0progeny1|ia64|ethereal.xml
EOF

pdk commit -m 'message'

# vim:set ai et sw=4 ts=4 tw=75:
