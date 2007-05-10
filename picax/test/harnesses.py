# $Progeny$
#
# Shared test harnesses.
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

"""This module contains shared test harnesses used by several other
tests."""

import os
import shutil
import unittest

import picax.config

class PackageBaseHarness(unittest.TestCase):
    "Shared harness sets up an environment for reading package info."

    default_part_size = 650000000

    def setUp(self):
        "Create a little repository for the package factory to read."

        if os.path.isdir("temp"):
            shutil.rmtree("temp")

        os.makedirs("temp/dists/foo/main/binary-i386")
        pkgs = open("temp/dists/foo/main/binary-i386/Packages", "w")
        pkgs.write("""Package: install-dcc
Priority: standard
Section: debian-installer
Installed-Size: 12
Maintainer: DCC Development Team <dcc-devel@lists.dccalliance.org>
Architecture: all
Version: 0.0.2
Depends: di-utils
Filename: ./packages/install-dcc_0.0.2_all.udeb
Size: 780
MD5sum: c99956bfab3494516241ea3429f8e7f9
Description: Install the DCC base system
 This package installs the DCC base system into the target in the
 first stage.

Package: lsb-base
Priority: extra
Section: misc
Installed-Size: 20
Maintainer: Chris Lawrence <lawrencc@debian.org>
Architecture: all
Source: lsb
Version: 2.0-7
Replaces: lsb (<< 2.0-6)
Depends: sed, ncurses-bin
Conflicts: lsb (<< 2.0-6)
Filename: ./packages/lsb-base_2.0-7_all.deb
Size: 8662
MD5sum: a16db2a9af668ef538c8dc2aea575768
Description: Linux Standard Base 2.0 init script functionality
 The Linux Standard Base (http://www.linuxbase.org/) is a standard
 core system that third-party applications written for Linux can
 depend upon.
 .
 This package only includes the init-functions shell library, which
 may be used by other packages' initialization scripts for console
 logging and other purposes.

Package: lsb-core
Priority: extra
Section: misc
Installed-Size: 128
Maintainer: Chris Lawrence <lawrencc@debian.org>
Architecture: i386
Source: lsb
Version: 2.0-7
Replaces: lsb (<< 2.0-2)
Provides: lsb-core-noarch, lsb-core-ia32
Depends: lsb-release, libz1, exim4 | mail-transport-agent, at, bc, binutils, bsdmainutils, cpio, cron, file, libc6-dev | libc-dev, locales, lpr, m4, make, man-db, mawk | gawk, ncurses-term, passwd, patch, pax, procps, psmisc, rsync, alien (>= 8.36), python (>> 2.2.2), debconf (>= 0.5) | debconf-2.0, lsb-base
Conflicts: python (>> 2.5), libutahglx1, lsb (<< 2.0-2)
Filename: ./packages/lsb-core_2.0-7_i386.deb
Size: 27450
MD5sum: d2093895a376a718cf7f917d80265e5b
Description: Linux Standard Base 2.0 core support package
 The Linux Standard Base (http://www.linuxbase.org/) is a standard
 core system that third-party applications written for Linux can
 depend upon.
 .
 This package provides an implementation of the core of version 2.0 of
 the Linux Standard Base for Debian on the Intel x86, Intel ia64
 (Itanium), IBM S390, and PowerPC 32-bit architectures with the Linux
 kernel.  Future revisions of the specification and this package may
 support the LSB on additional architectures and kernels.
 .
 The intent of this package is to provide a best current practice way
 of installing and running LSB packages on Debian GNU/Linux.  Its
 presence does not imply that we believe that Debian fully complies
 with the Linux Standard Base, and should not be construed as a
 statement that Debian is LSB-compliant.

Package: lsb-cxx
Priority: extra
Section: misc
Installed-Size: 12
Maintainer: Chris Lawrence <lawrencc@debian.org>
Architecture: i386
Source: lsb
Version: 2.0-7
Provides: lsb-cxx-noarch, lsb-cxx-ia32
Depends: lsb-core, libstdc++5
Filename: ./packages/lsb-cxx_2.0-7_i386.deb
Size: 6466
MD5sum: 4c5fb71fede71b15819971e9772cc602
Description: Linux Standard Base 2.0 C++ support package
 The Linux Standard Base (http://www.linuxbase.org/) is a standard
 core system that third-party applications written for Linux can
 depend upon.
 .
 This package provides an implementation of version 2.0 of the Linux
 Standard Base C++ (CXX) specification for Debian on the Intel x86,
 Intel ia64 (Itanium), IBM S390, and PowerPC 32-bit architectures with
 the Linux kernel.  Future revisions of the specification and this
 package may support the LSB on additional architectures and kernels.
 .
 The intent of this package is to provide a best current practice way
 of installing and running LSB packages on Debian GNU/Linux.  Its
 presence does not imply that we believe that Debian fully complies
 with the Linux Standard Base, and should not be construed as a
 statement that Debian is LSB-compliant.

Package: lsb-graphics
Priority: extra
Section: misc
Installed-Size: 12
Maintainer: Chris Lawrence <lawrencc@debian.org>
Architecture: i386
Source: lsb
Version: 2.0-7
Provides: lsb-graphics-noarch, lsb-graphics-ia32
Depends: lsb-core, xlibmesa3-gl | libgl1, xlibs
Filename: ./packages/lsb-graphics_2.0-7_i386.deb
Size: 6476
MD5sum: e7e3728acb36a320e91fc7dc81cfb0a9
Description: Linux Standard Base 2.0 graphics support package
 The Linux Standard Base (http://www.linuxbase.org/) is a standard
 core system that third-party applications written for Linux can
 depend upon.
 .
 This package provides an implementation of version 2.0 of the Linux
 Standard Base graphics specification for Debian on the Intel x86,
 Intel ia64 (Itanium), IBM S390, and PowerPC 32-bit architectures with
 the Linux kernel.  Future revisions of the specification and this
 package may support the LSB on additional architectures and kernels.
 .
 The intent of this package is to provide a best current practice way
 of installing and running LSB packages on Debian GNU/Linux.  Its
 presence does not imply that we believe that Debian fully complies
 with the Linux Standard Base, and should not be construed as a
 statement that Debian is LSB-compliant.

Package: lsb
Priority: extra
Section: misc
Installed-Size: 12
Maintainer: Chris Lawrence <lawrencc@debian.org>
Architecture: all
Version: 2.0-7
Depends: lsb-core, lsb-graphics, lsb-cxx
Filename: ./packages/lsb_2.0-7_all.deb
Size: 6424
MD5sum: fb0948c707aadc493247167ef470238e
Description: Linux Standard Base 2.0 support package
 The Linux Standard Base (http://www.linuxbase.org/) is a standard
 core system that third-party applications written for Linux can
 depend upon.
 .
 This package provides an implementation of all modules of version 2.0
 of the Linux Standard Base for Debian on the Intel x86, Intel ia64
 (Itanium), IBM S390, and PowerPC 32-bit architectures with the Linux
 kernel.  Future revisions of the specification and this package may
 support the LSB on additional architectures and kernels.
 .
 The intent of this package is to provide a best current practice way
 of installing and running LSB packages on Debian GNU/Linux.  Its
 presence does not imply that we believe that Debian fully complies
 with the Linux Standard Base, and should not be construed as a
 statement that Debian is LSB-compliant.

""")
        pkgs.close()

        os.makedirs("temp/dists/foo/main/source")
        srcs = open("temp/dists/foo/main/source/Sources", "w")
        srcs.write("""Package: install-dcc
Binary: install-dcc
Version: 0.0.2
Maintainer: DCC Development Team <dcc-devel@lists.dccalliance.org>
Build-Depends: debhelper (>= 4.2.0)
Architecture: all
Standards-Version: 3.6.1
Format: 1.0
Directory: ./packages
Files:
 ca4cb6765850ac19801b4eb40840da35 330 install-dcc_0.0.2.dsc
 a28401fd94467cf963d466efaf2e777c 995 install-dcc_0.0.2.tar.gz
Uploaders: Jeff Licquia <licquia@progeny.com>

Package: lsb
Binary: lsb-core, lsb, lsb-cxx, lsb-base, lsb-graphics
Version: 2.0-7
Maintainer: Chris Lawrence <lawrencc@debian.org>
Build-Depends: debhelper (>= 4.1.13), po-debconf (>= 0.5.0)
Architecture: any
Standards-Version: 3.6.1
Format: 1.0
Directory: ./packages
Files:
 d46eceef245a8c2e96469f8f090b1114 548 lsb_2.0-7.dsc
 c59bfd01160139b905350a971b45fa2b 28444 lsb_2.0-7.tar.gz

""")
        srcs.close()

        release = open("temp/dists/foo/Release", "w")
        release.write("""Origin: Progeny
Label: Progeny
Suite: foo
Version: 1.0
Codename: foo
Date: Mon, 06 Jun 2005 02:22:42 UTC
Architectures: i386
Components: main
Description: Test repository
""")
        release.close()

        for arch in ("i386", "source"):
            if arch == "source":
                path_component = arch
            else:
                path_component = "binary-%s" % (arch,)

            release = open(
                "temp/dists/foo/main/%s/Release" % (path_component), "w")
            release.write("""Archive: foo
Version: 1.0
Component: main
Origin: Progeny
Label: Progeny
Architecture: %s
""" % (arch,))
            release.close()

        os.mkdir("temp/packages")
        for f in ("install-dcc_0.0.2.dsc", "install-dcc_0.0.2.tar.gz",
                  "install-dcc_0.0.2_all.udeb",
                  "install-dcc_0.0.2_i386.changes",
                  "lsb-base_2.0-7_all.deb",
                  "lsb-core_2.0-7_i386.deb", "lsb-cxx_2.0-7_i386.deb",
                  "lsb-graphics_2.0-7_i386.deb", "lsb_2.0-7.dsc",
                  "lsb_2.0-7.tar.gz", "lsb_2.0-7_all.deb"):
            t = open("temp/packages/" + f, "w")
            t.write("123")
            t.close()

        picax.config.handle_args(
            ["--part-size=%d" % (self.default_part_size,),
             "temp", "foo", "main"])

    def tearDown(self):
        "Remove the little repository and any other temporary directories."

        shutil.rmtree("temp")

        for temp_path in ("temp2", "temp3", "temp4"):
            if os.path.isdir(temp_path):
                shutil.rmtree(temp_path)

# vim:set ai et sw=4 ts=4 tw=75:
