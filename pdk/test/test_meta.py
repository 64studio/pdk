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

from pdk.test.utest_util import Test
from pdk.meta import Entity
from sets import Set

class TestEntity(Test):
    def test_filter_by_domain(self):
        entity = Entity(None, None)
        entity['deb', 'a'] = 1
        entity['pdk', 'b'] = 2
        entity['deb', 'c'] = 3
        entity['ldap', 'd'] = 4

        actual = Set(entity.iter_by_domains(('deb', 'ldap', 'notfound')))
        expected = Set([ ('a', 1), ('c', 3), ('d', 4) ])
        self.assert_equals(expected, actual)

# vim:set ai et sw=4 ts=4 tw=75:
