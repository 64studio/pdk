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

from pdk.package import deb
from pdk.media import PackageMediaItems, Splitter, BREAK
from pdk.test.utest_util import Test, MockPackage

class SizedDeb(MockPackage):
    def __init__(self, name, version, size):
        super(SizedDeb, self).__init__(name, version, deb, arch = 'i386',
                                 extras = {('pdk', 'size'): size})

class TestPackageMediaItems(Test):
    def test_do_nothing(self):
        items = PackageMediaItems([])
        output = list(items)
        self.assert_equal([], output)

    def test_packages(self):
        package1 = SizedDeb('a', '1', '10')
        package2 = SizedDeb('b', '1', '20')

        items = PackageMediaItems([package1, package2])
        output = [ o for o in items ]
        self.assert_equal(output, [ (10, package1), (20, package2) ])

class TestSplitter(Test):
    def test_do_nothing(self):
        splitter = Splitter([], 0)
        volumes = list(splitter.iter_volumes())
        self.assert_equal([], volumes)

    def test_exact(self):
        package1 = SizedDeb('a', '1', '10')
        package2 = SizedDeb('b', '1', '20')
        packages = PackageMediaItems([package1, package2])
        splitter = Splitter(packages, 30)
        volumes = list(splitter.iter_volumes())
        self.assert_equal([package1, package2], volumes)

    def test_undersized(self):
        package1 = SizedDeb('a', '1', '10')
        package2 = SizedDeb('b', '1', '20')
        packages = PackageMediaItems([package1, package2])
        splitter = Splitter(packages, 31)
        volumes = list(splitter.iter_volumes())
        self.assert_equal([package1, package2], volumes)

    def test_overflow_exact(self):
        package1 = SizedDeb('a', '1', '10')
        package2 = SizedDeb('b', '1', '20')
        package3 = SizedDeb('c', '1', '25')
        packages = PackageMediaItems([package1, package2, package3])
        splitter = Splitter(packages, 30)
        volumes = list(splitter.iter_volumes())
        self.assert_equal([package1, package2, BREAK, package3], volumes)

    def test_overflow_under(self):
        package1 = SizedDeb('a', '1', '10')
        package2 = SizedDeb('b', '1', '20')
        package3 = SizedDeb('c', '1', '25')
        packages = PackageMediaItems([package1, package2, package3])
        splitter = Splitter(packages, 31)
        volumes = list(splitter.iter_volumes())
        self.assert_equal([package1, package2, BREAK, package3], volumes)

    def test_multiple_overflow(self):
        package1 = SizedDeb('a', '1', '10')
        package2 = SizedDeb('b', '1', '20')
        package3 = SizedDeb('c', '1', '25')
        package4 = SizedDeb('d', '1', '10')
        packages = PackageMediaItems([package1, package2, package3,
                                      package4])
        splitter = Splitter(packages, 30)
        volumes = list(splitter.iter_volumes())
        self.assert_equal([package1, package2, BREAK, package3, BREAK,
                           package4], volumes)

# vim:set ai et sw=4 ts=4 tw=75:
