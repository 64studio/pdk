# $Progeny$
#
# Test picax.newrepo.
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

"This module tests the picax.newrepo module."

import os

import picax.newrepo
import picax.package

from picax.test.harnesses import PackageBaseHarness

class TestNewRepositoryProcess(PackageBaseHarness):
    "Test that the process of creating a repository has no errors."

    def testNewRepositoryProcess(self):
        "Test a new repository."

        index = open("temp/dists/foo/main/binary-i386/Packages")
        factory = picax.package.PackageFactory(index, "temp", "foo",
                                               "main")
        packages = factory.get_packages()
        index.close()

        os.mkdir("temp2")
        newrepo = picax.newrepo.NewRepository(packages, "temp2")
        newrepo.write_repo()

        self.failUnless(os.path.exists("temp2/packages"),
                        "no package pool directory found")
        self.failUnless(
            os.path.exists("temp2/dists/foo/main/binary-i386/Packages"),
            "no package index found")

class TestNewRepositoryResults(PackageBaseHarness):
    "Test that the resulting repository is correct."

    def setUp(self):
        "Besides setting up the base harness, set up the new repository."

        PackageBaseHarness.setUp(self)

        index = open("temp/dists/foo/main/binary-i386/Packages")
        factory = picax.package.PackageFactory(index, "temp", "foo",
                                               "main")
        packages = factory.get_packages()
        index.close()

        os.mkdir("temp2")
        newrepo = picax.newrepo.NewRepository(packages, "temp2")
        newrepo.write_repo()

    def testTopRelease(self):
        "Make sure there's a toplevel Release file."

        self.failUnless(os.path.exists("temp2/dists/foo/Release"),
                        "no toplevel Release file found")

# vim:set ai et sw=4 ts=4 tw=75:
