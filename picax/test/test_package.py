# $Progeny$
#
# Test picax.package.
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

"""This module tests the picax.package module."""

import os

import picax.package

from picax.test.harnesses import PackageBaseHarness

package_factory = picax.package.PackageFactory

class TestFactory(PackageBaseHarness):
    "Test that the factories are able to read the index files."

    def testBinary(self):
        "Test a binary package index."

        index = open("temp/dists/foo/main/binary-i386/Packages")
        factory = package_factory(index, "temp", "foo", "main")
        packages = factory.get_packages()
        assert len(packages) > 0
        index.close()

    def testSource(self):
        "Test a source package index."

        index = open("temp/dists/foo/main/source/Sources")
        factory = package_factory(index, "temp", "foo", "main")
        packages = factory.get_packages()
        assert len(packages) > 0
        index.close()

    def testRightType(self):
        "Make sure the right packages have the right package objects."

        udeb_list = ["install-dcc"]

        index = open("temp/dists/foo/main/binary-i386/Packages")
        factory = package_factory(index, "temp", "foo", "main")

        for pkg in factory:
            if pkg["Package"] in udeb_list:
                assert isinstance(pkg, picax.package.UBinaryPackage)
            else:
                assert isinstance(pkg, picax.package.BinaryPackage)

        index.close()
        index = open("temp/dists/foo/main/source/Sources")
        factory = package_factory(index, "temp", "foo", "main")

        for pkg in factory:
            assert isinstance(pkg, picax.package.SourcePackage)

class TestPackage(PackageBaseHarness):
    "Test features of the package classes themselves."

    def testPackageLines(self):
        """Test that the package index data returned is identical to
        what is read from the index."""

        lines = [ "Package: install-dcc\n",
                  "Priority: standard\n",
                  "Section: debian-installer\n",
                  "Installed-Size: 12\n",
"Maintainer: DCC Development Team <dcc-devel@lists.dccalliance.org>\n",
                  "Architecture: all\n",
                  "Version: 0.0.2\n",
                  "Depends: di-utils\n",
                  "Filename: ./packages/install-dcc_0.0.2_all.udeb\n",
                  "Size: 780\n",
                  "MD5sum: c99956bfab3494516241ea3429f8e7f9\n",
                  "Description: Install the DCC base system\n",
" This package installs the DCC base system into the target in the\n",
                  " first stage.\n" ]

        index = open("temp/dists/foo/main/binary-i386/Packages")
        factory = package_factory(index, "temp", "foo", "main")
        pkg = factory.get_next_package()
        index.close()

        read_lines = pkg.get_lines()
        assert len(read_lines) == len(lines)

        for (l1, l2) in \
                [(read_lines[i], lines[i]) for i in range(0, len(lines))]:
            self.failUnless(l1 == l2,
                            "unequal lines: expected '%s', got '%s'"
                            % (l2, l1))

    def testCalculatedField(self):
        "Test that calculated fields work properly."

        index = open("temp/dists/foo/main/binary-i386/Packages")
        factory = package_factory(index, "temp", "foo",
                                               "main")
        pkg = factory.get_next_package()
        index.close()

        size = pkg["Package-Size"]
        self.failUnless(size == 3,
                        "wrong binary package size: %d" % (size,))

        index = open("temp/dists/foo/main/source/Sources")
        factory = package_factory(index, "temp", "foo",
                                               "main")
        pkg = factory.get_next_package()
        index.close()

        size = pkg["Package-Size"]
        self.failUnless(size == 6,
                        "wrong source package size: %d" % (size,))

    def testSourceInfo(self):
        "Test that proper source information is returned."

        index = open("temp/dists/foo/main/binary-i386/Packages")
        factory = package_factory(index, "temp", "foo",
                  "main")
        pkg = factory.get_next_package()
        index.close()

        (srcname, srcversion) = pkg.get_source_info()
        self.failUnless(srcname == "install-dcc" and srcversion == "0.0.2",
                        "source info incorrect: got %s, %s"
                        % (srcname, srcversion))

    def testLink(self):
        "Test that proper links are created when requested."

        index = open("temp/dists/foo/main/binary-i386/Packages")
        factory = package_factory(index, "temp", "foo",
                                               "main")
        pkg = factory.get_next_package()
        index.close()

        os.mkdir("temp2")
        pkg.link("temp2")

        assert os.path.exists("temp2/packages/install-dcc_0.0.2_all.udeb")

# vim:set ai et sw=4 ts=4 tw=75:
