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

# Unit test the workspace commands.

. atest/test_lib.sh

pdk workspace && fail 'Should have failed.'

verify_new_workspace() {
    dir="$1"
    (cd $dir; find -not -type d) | LANG=C sort | grep -v git/hooks >actual.txt
    diff -u - actual.txt <<EOF
./.git
./etc/git/HEAD
./etc/git/config
./etc/git/description
./etc/git/info/exclude
./etc/schema
EOF
    [ "$(readlink $dir/.git)" = etc/git ]
    [ -e $dir/.git/description ]
    [ 6 = "$(cat $dir/etc/schema)" ]
}

pdk workspace create || status=$?
test "$status" == 2 || bail "Expected command line error"

pdk workspace create foo
verify_new_workspace foo
rm -rf foo

# make sure the alias works too
pdk create workspace foo
verify_new_workspace foo
rm -rf foo

pdk workspace create exists
pdk workspace create exists \
    && fail "Shouldn't be able to create over an existing workspace."

# vim:set ai et sw=4 ts=4 tw=75:
