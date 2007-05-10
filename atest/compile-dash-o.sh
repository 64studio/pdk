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

# Check that repogen -o works.

. atest/utils/repogen-fixture.sh

set_up_repogen_fixture compile

pushd compile

    pdk repogen -o arbitrary product.xml
    [ -d ./repo ] && fail "repo dir should not exist"
    [ -d ./arbitrary ] || fail "dir 'arbitrary' should exist."

    mkdir tmp
    cd tmp
    pdk repogen -o intmp ../product.xml
    cd -

    [ -d ./repo ] && fail "repo dir should not exist"
    [ -d ./tmp/intmp ] || fail "dir 'tmp/intmp' should exist."

    diff -u -r arbitrary tmp/intmp

    pdk repogen product.xml
    diff -u -r repo arbitrary

popd

# vim:set ai et sw=4 ts=4 tw=75:
