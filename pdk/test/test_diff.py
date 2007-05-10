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

"""Unit test for semantic diff operations"""
from pdk.test.utest_util import Test, MockPackage
from pdk.package import deb
from sets import Set

from pdk.semdiff import iter_diffs

class TestDiff(Test):
    def test_diff_same(self):
        a = MockPackage('a', '1', deb, arch = 'i386')
        b = MockPackage('b', '1', deb, arch = 'i386')
        list1 = [ a, b ]
        list2 = list1[:]
        list2.reverse()
        diffs = iter_diffs(list1, list2)
        expected = Set([ ('unchanged', a, a),
                         ('unchanged', b, b) ])
        self.assert_equals_long(expected, Set(diffs))

    def test_diff_add(self):
        a = MockPackage('a', '1', deb, arch = 'i386')
        b = MockPackage('b', '1', deb, arch = 'i386')
        list1 = []
        list2 = [ a, b ]
        diffs = iter_diffs(list1, list2)
        expected = Set([ ('add', a, None),
                         ('add', b, None) ])
        self.assert_equals_long(expected, Set(diffs))

    def test_diff_remove(self):
        a = MockPackage('a', '1', deb, arch = 'i386')
        b = MockPackage('b', '1', deb, arch = 'i386')
        list1 = [ a, b]
        list2 = []
        diffs = iter_diffs(list1, list2)
        expected = Set([ ('drop', a, None),
                         ('drop', b, None) ])
        self.assert_equals_long(expected, Set(diffs))

    def test_diff_upgrade(self):
        a1 = MockPackage('a', '1', deb, arch = 'i386')
        a2 = MockPackage('a', '2', deb, arch = 'i386')
        list1 = [ a1 ]
        list2 = [ a2 ]
        diffs = iter_diffs(list1, list2)
        expected = Set([ ('upgrade', a1, a2) ])
        self.assert_equals_long(expected, Set(diffs))

    def test_diff_downgrade(self):
        a1 = MockPackage('a', '1', deb, arch = 'i386')
        a2 = MockPackage('a', '2', deb, arch = 'i386')
        list1 = [ a2 ]
        list2 = [ a1 ]
        diffs = iter_diffs(list1, list2)
        expected = Set([ ('downgrade', a2, a1) ])
        self.assert_equals_long(expected, Set(diffs))

    def test_diff_with_distractions(self):
        a = MockPackage('a', '1', deb, arch = 'i386')
        b = MockPackage('b', '1', deb, arch = 'i386')
        a_arm = MockPackage('a', '1', deb, arch = 'arm')
        c = MockPackage('c', '1', deb, arch = 'i386')
        list1 = [ a, b ]
        list2 = list1[:]
        list2.reverse()
        list2.append(c)
        list1.append(a_arm)
        diffs = iter_diffs(list1, list2)
        expected = Set([ ('unchanged', a, a),
                         ('unchanged', b, b),
                         ('add', c, None),
                         ('drop', a_arm, None) ])
        diffs = list(diffs)
        diffs.sort()
        expected = list(expected)
        expected.sort()
        self.assert_equals_long(expected, diffs)

# vim:set ai et sw=4 ts=4 tw=75:
