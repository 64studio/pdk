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

# Test having git and pdk cache-pull talk to a real apache2 server.

cat >bin/ssh <<EOF
#!/bin/sh
# A mock ssh.
# this script tested with rsync
host="\$1"
PS4='-- ssh \$host: '
shift
if [ -z "\$1" ]; then
    echo >&2 "No ssh command given. Login not available."
    exit 1
fi
if [ $host != "localhost" ]; then
    echo >&2 "Only localhost allowed!"
    exit 1
fi
set -e
set -x
cd $tmp_dir
"\$@"
EOF
chmod +x bin/ssh

. atest/utils/repogen-fixture.sh

pdk workspace create production
pdk workspace create alice
pdk workspace create bob

for dir in alice bob; do
    pushd $dir
        cat >etc/channels.xml <<EOF
<?xml version="1.0"?>
<channels>
  <production>
    <type>source</type>
    <path>$tmp_dir/production</path>
  </production>
</channels>
EOF
    popd
done

pushd alice
    cat >somefile <<EOF
a
EOF
    pdk add somefile
    pdk commit -m 'Initial Alice Commit'

    pdk push production
popd

pushd bob
    pdk pull production
    cat >>somefile <<EOF
c
EOF
    pdk commit -m 'Initial Bob Commit'
    # don't push yet
popd

pushd alice
    cat >>somefile <<EOF
b
EOF
    pdk commit -m 'Alice Modification'
    pdk push production
popd

pushd bob
    # bob's HEAD will be out of date. Should fail.
    status=0
    pdk push production 2>errors.txt || status=$?
    cat errors.txt
    [ $status = 4 ] || fail 'expected error 4 here'
    grep -i -q 'out.of.date' errors.txt \
        || fail 'expected an error about workspace being out of date.'
popd

# vim:set ai et sw=4 ts=4 tw=75:
