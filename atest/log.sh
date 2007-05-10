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

# log should show an ordered list of commit logs

. atest/utils/repogen-fixture.sh

set_up_repogen_fixture a

pdk workspace create b
pushd a
    pdk add progeny.com/apache.xml
    pdk commit -m "Initial Commit"

    pdk repogen progeny.com/apache.xml

popd

pushd b
    cat >etc/channels.xml <<EOF
<?xml version="1.0"?>
<channels>
  <a>
    <type>source</type>
    <path>$tmp_dir/a</path>
  </a>
</channels>
EOF

    pdk pull a
    pdk log | grep "Initial Commit" \
        || fail 'Should find initial commit'

    echo '<!-- comment -->' >>progeny.com/apache.xml
    pdk commit -m 'a local change'

    pdk log | grep "Initial Commit" \
        || fail 'Should still find initial commit'
    pdk log | grep "a local change" \
        || fail 'Should find local change.'

    pdk log a | grep "Initial Commit" \
        && fail 'Should not find initial commit'
    pdk log a | grep "a local change" \
        || fail 'Should still find local change.'
popd

# vim:set ai et sw=4 ts=4 tw=75:
