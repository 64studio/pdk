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

# Test pdk semdiff in compare two files mode.

. atest/utils/semdiff-fixture.sh

set_up_semdiff_fixture test-semdiff
cd test-semdiff

# --------------------------------
# Test semdiff with rpms.
# --------------------------------

# once without --show-unchanged
pdk semdiff -m timex-12.xml timex-12.xml \
    | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
EOF

pdk semdiff --show-unchanged -m timex-12.xml timex-12.xml \
    | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
unchanged|rpm|adjtimex|1.13-12|1.13-12|i386|timex-12.xml
unchanged|srpm|adjtimex|1.13-12|1.13-12|x86_64|timex-12.xml
EOF

pdk semdiff --show-unchanged -m timex-12.xml timex-13.xml \
    | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
upgrade|rpm|adjtimex|1.13-12|1.13-13|i386|timex-13.xml
upgrade|srpm|adjtimex|1.13-12|1.13-13|x86_64|timex-13.xml
EOF

pdk semdiff --show-unchanged -m timex-13.xml timex-12.xml \
    | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
downgrade|rpm|adjtimex|1.13-13|1.13-12|i386|timex-12.xml
downgrade|srpm|adjtimex|1.13-13|1.13-12|x86_64|timex-12.xml
EOF

pdk semdiff --show-unchanged -m timex-12.xml timex-12-nosrc.xml \
    | grep -v ^unchanged \
    | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
drop|srpm|adjtimex|1.13-12|x86_64|timex-12-nosrc.xml
EOF

pdk semdiff --show-unchanged -m timex-12-nosrc.xml timex-12.xml \
    | grep -v ^unchanged \
    | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
add|srpm|adjtimex|1.13-12|x86_64|timex-12.xml
EOF

# --------------------------------
# Test semdiff with debs.
# --------------------------------

pdk semdiff --show-unchanged -m ethereal1.xml ethereal1.xml \
    | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
unchanged|deb|ethereal-common|0.9.13-1.0progeny1|0.9.13-1.0progeny1|ia64|ethereal1.xml
unchanged|deb|ethereal-dev|0.9.13-1.0progeny1|0.9.13-1.0progeny1|ia64|ethereal1.xml
unchanged|deb|ethereal|0.9.13-1.0progeny1|0.9.13-1.0progeny1|ia64|ethereal1.xml
unchanged|deb|tethereal|0.9.13-1.0progeny1|0.9.13-1.0progeny1|ia64|ethereal1.xml
unchanged|dsc|ethereal|0.9.13-1.0progeny1|0.9.13-1.0progeny1|any|ethereal1.xml
EOF

pdk semdiff --show-unchanged -m ethereal1.xml ethereal2.xml \
    | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
upgrade|deb|ethereal-common|0.9.13-1.0progeny1|0.9.13-1.0progeny2|ia64|ethereal2.xml
upgrade|deb|ethereal-dev|0.9.13-1.0progeny1|0.9.13-1.0progeny2|ia64|ethereal2.xml
upgrade|deb|ethereal|0.9.13-1.0progeny1|0.9.13-1.0progeny2|ia64|ethereal2.xml
upgrade|deb|tethereal|0.9.13-1.0progeny1|0.9.13-1.0progeny2|ia64|ethereal2.xml
upgrade|dsc|ethereal|0.9.13-1.0progeny1|0.9.13-1.0progeny2|any|ethereal2.xml
EOF

pdk semdiff --show-unchanged -m ethereal2.xml ethereal1.xml \
    | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
downgrade|deb|ethereal-common|0.9.13-1.0progeny2|0.9.13-1.0progeny1|ia64|ethereal1.xml
downgrade|deb|ethereal-dev|0.9.13-1.0progeny2|0.9.13-1.0progeny1|ia64|ethereal1.xml
downgrade|deb|ethereal|0.9.13-1.0progeny2|0.9.13-1.0progeny1|ia64|ethereal1.xml
downgrade|deb|tethereal|0.9.13-1.0progeny2|0.9.13-1.0progeny1|ia64|ethereal1.xml
downgrade|dsc|ethereal|0.9.13-1.0progeny2|0.9.13-1.0progeny1|any|ethereal1.xml
EOF

pdk semdiff --show-unchanged -m ethereal1.xml ethereal1-missing.xml \
    | grep -v ^unchanged \
    | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
drop|deb|ethereal|0.9.13-1.0progeny1|ia64|ethereal1-missing.xml
EOF

pdk semdiff --show-unchanged -m ethereal1-missing.xml ethereal1.xml \
    | grep -v ^unchanged \
    | LANG=C sort >semdiff.txt
diff -u - semdiff.txt <<EOF
add|deb|ethereal|0.9.13-1.0progeny1|ia64|ethereal1.xml
EOF

# vim:set ai et sw=4 ts=4 tw=75:
