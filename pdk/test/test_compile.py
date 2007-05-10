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

import os
from sets import Set
from pdk.test.utest_util import TempDirTest
from pdk.cache import Cache
from pdk.util import pjoin, cpath

from pdk.repogen import DebianReleaseWriter, LazyWriter, \
     DebianDirectPoolRepo, DebianPoolInjector, Compiler

__revision__ = "$Progeny$"

set_up_cache = '''
mkdir -p cache/sha-1/9d
cat >./cache/sha-1/9d/sha-1:9d26152e78ca33a3d435433c67644b52ae4c670c.header <<EOF
Format: 1.0
Source: apache2
Version: 2.0.53-5
Binary: apache2-doc, apache2-mpm-threadpool, libapr0, apache2-mpm-prefork, apache2, apache2-mpm-worker, libapr0-dev, apache2-common, apache2-prefork-dev, apache2-utils, apache2-mpm-perchild, apache2-threaded-dev
Maintainer: Debian Apache Maintainers <debian-apache@lists.debian.org>
Architecture: any
Standards-Version: 3.6.1.0
Build-Depends: debhelper (>> 4.1.1), libssl-dev, openssl, bzip2, autoconf, autotools-dev, libtool, libdb4.2-dev, zlib1g-dev, libpcre3-dev, libldap2-dev, libexpat1-dev, mawk
Build-Conflicts: libgdbm-dev
Uploaders: Tollef Fog Heen <tfheen@debian.org>, Thom May <thom@debian.org>, Fabio M. Di Nitto <fabbione@fabbione.net>, Daniel Stone <daniels@debian.org>, Adam Conrad <adconrad@0c3.net>
Files:
 40507bf19919334f07355eda2df017e5 6925351 apache2_2.0.53.orig.tar.gz
 0d060d66b3a1e6ec0b9c58e995f7b9f7 105448 apache2_2.0.53-5.diff.gz
EOF

mkdir -p cache/sha-1/b7
cat >./cache/sha-1/b7/sha-1:b7d31cf9a160c3aadaf5f1cd86cdc8762b3d4b1b.header <<EOF
Package: apache2-common
Version: 2.0.53-5
Section: net
Priority: optional
Architecture: i386
Depends: libc6 (>= 2.3.2.ds1-4), libdb4.2, libexpat1 (>= 1.95.8), debconf, debianutils (>= 1.6), mime-support, openssl, net-tools, ssl-cert (>= 1.0-7), libmagic1, libgcc1 (>= 1:3.3.5), apache2-utils (= 2.0.53-5)
Suggests: apache2-doc, lynx | www-browser
Installed-Size: 1915
Maintainer: Debian Apache Maintainers <debian-apache@lists.debian.org>
Source: apache2
Description: next generation, scalable, extendable web server
 Apache v2 is the next generation of the omnipresent Apache web server. This
 version - a total rewrite - introduces many new improvements, such as
 threading, a new API, IPv6 support, request/response filtering, and more.
 .
 It is also considerably faster, and can be easily extended to provide services
 other than http.
 .
 This package contains all the standard apache2 modules, including SSL support.
 However, it does *not* include the server itself; for this you need to
 install one of the apache2-mpm-* packages; such as worker or prefork.
EOF

'''

class CacheFixture(TempDirTest):
    def set_up(self):
        super(CacheFixture, self).set_up()
        os.system(set_up_cache)
        self.cache = Cache(pjoin(self.work_dir, 'cache'))
        self.compiler = Compiler(self.cache)

class DebianPoolFixture(CacheFixture):
    def set_up(self):
        super(DebianPoolFixture, self).set_up()
        self.repo = DebianDirectPoolRepo(pjoin(self.work_dir, '.'),
                                         'dists/happy',
                                         Set(['i386', 'sparc', 'source']),
                                         Set(['main', 'contrib']),
                                         os.path.join(self.work_dir,
                                                      'repo'))

class TestDebianPoolRepo(DebianPoolFixture):
    def test_repo_and_tmp_dir(self):
        self.assert_equal(pjoin(self.work_dir, 'repo'), self.repo.repo_dir)
        self.assert_equal(pjoin(self.work_dir, 'tmp', 'dists', 'happy'),
                          self.repo.tmp_dir)

    def test_lazy_writer(self):
        full_name = pjoin(self.repo.tmp_dir, 'asdf')
        handle = LazyWriter(full_name)
        print >> handle, 'hello'
        handle.close()
        self.fail_unless(os.path.exists(full_name))
        handle = open(full_name)
        self.assert_equal("hello\n", handle.read())
        handle.close()

    def test_create_directories(self):
        all_dirs = self.repo.get_all_dirs()
        assert cpath('repo', 'dists', 'happy', 'main', 'binary-i386') \
               in all_dirs
        assert cpath('repo', 'dists', 'happy', 'main', 'binary-sparc') \
               in all_dirs
        assert cpath('repo', 'dists', 'happy', 'main', 'source') \
               in all_dirs
        assert cpath('repo', 'dists', 'happy', 'contrib', 'binary-i386') \
               in all_dirs
        assert cpath('repo', 'dists', 'happy', 'contrib', 'binary-sparc') \
               in all_dirs
        assert cpath('repo', 'dists', 'happy', 'contrib', 'source') \
               in all_dirs
        self.assert_equals(6, len(all_dirs))

        self.repo.make_all_dirs()
        for expected_dir in all_dirs:
            assert os.path.isdir(expected_dir)

    def test_write_releases(self):
        calls = Set()
        outer = Set()

        class MockWriter(object):
            def write(self, handle, section, arch):
                calls.add((handle.name, section, arch))

            def write_outer(self, handle):
                outer.add(handle.name)

        writer = MockWriter()

        self.repo.write_releases(writer)

        self.assert_equals(6, len(calls))

        def make_tuple(section, arch):
            release_path = pjoin(self.repo.get_one_dir(section, arch),
                                 'Release')
            return (release_path, section, arch)

        assert make_tuple('main', 'i386') in calls
        assert make_tuple('main', 'sparc') in calls
        assert make_tuple('main', 'source') in calls
        assert make_tuple('contrib', 'i386') in calls
        assert make_tuple('contrib', 'sparc') in calls
        assert make_tuple('contrib', 'source') in calls

        release_path = pjoin(self.repo.repo_dir, 'dists', 'happy',
                             'Release')
        expected = Set([release_path])
        self.assert_equal(expected, outer)

class TestDebianPoolInjector(DebianPoolFixture):
    def set_up(self):
        super(TestDebianPoolInjector, self).set_up()

        blob_id = 'sha-1:b7d31cf9a160c3aadaf5f1cd86cdc8762b3d4b1b'
        self.bin = self.cache.load_package(blob_id, 'deb')
        self.bin_injector = DebianPoolInjector(self.cache, self.bin,
                                               'main', self.repo.repo_dir)

        blob_id = 'sha-1:9d26152e78ca33a3d435433c67644b52ae4c670c'
        self.src = self.cache.load_package(blob_id, 'dsc')
        self.src_injector = DebianPoolInjector(self.cache, self.src,
                                               'main', self.repo.repo_dir)

    def test_pool_location(self):
        location = self.bin_injector.get_pool_location()
        expected = pjoin(self.repo.repo_dir, 'pool', 'main', 'a',
                         'apache2', self.bin.filename)
        self.assert_equals_long(expected, location)

    def test_extra_pool_locations(self):
        self.assert_equal({},
                          self.bin_injector.get_extra_pool_locations())

        src_package_path = self.src_injector.get_pool_location()
        src_package_dir = pjoin(src_package_path, '..')
        extras = {}
        extras.update(dict([ (pjoin(src_package_dir, filename), blob_id)
                             for blob_id, dummy, filename
                             in self.src.pdk.extra_file ]))
        actual_extras = self.src_injector.get_extra_pool_locations()
        self.assert_equals_long(extras, actual_extras)

    def test_relative_pool_path(self):
        actual_path = "pool/main/a/apache2"
        self.assert_equals_long(self.bin_injector.get_relative_pool_path(),
                                actual_path)
        self.assert_equals_long(self.src_injector.get_relative_pool_path(),
                                actual_path)

    def test_get_links(self):
        package_location = self.src_injector.get_pool_location()
        package_dir = pjoin(self.src_injector.get_pool_location(), '..')
        files = [ t[0] for t in self.src.pdk.extra_file ]
        files.sort()
        expected = { package_location: self.src.blob_id,
                     pjoin(package_dir, 'apache2_2.0.53-5.diff.gz'):
                     'md5:0d060d66b3a1e6ec0b9c58e995f7b9f7',
                     pjoin(package_dir, 'apache2_2.0.53.orig.tar.gz'):
                     'md5:40507bf19919334f07355eda2df017e5' }
        actual = self.src_injector.get_links()
        self.assert_equals_long(expected, actual)

class TestReleaseWriter(TempDirTest):
    def set_up(self):
        super(self.__class__, self).set_up()
        self.search_path = pjoin(self.work_dir, 'repo', 'stuff')
        release_time = 'Wed, 22 Mar 2005 21:20:00 UTC'
        contents = { ('apt-deb', 'archive'): 'stable',
                     ('apt-deb', 'version'): '3.0r4',
                     ('apt-deb', 'origin'): 'Debian',
                     ('apt-deb', 'label'): 'Debian2',
                     ('apt-deb', 'suite'): 'happy',
                     ('apt-deb', 'codename'): 'woody',
                     ('apt-deb', 'date'): release_time,
                     ('apt-deb', 'description'): 'Hello World!' }
        self.writer = DebianReleaseWriter(contents, ['i386', 'alpha'],
                                          ['main', 'contrib'],
                                          self.search_path)

    def test_write_inner_release(self):
        dest = LazyWriter(pjoin(self.work_dir, 'Release'))
        self.writer.write(dest, 'main', 'i386')
        dest.close()
        expected = """Archive: stable
Version: 3.0r4
Component: main
Origin: Debian
Label: Debian2
Architecture: i386
"""
        actual = self.read_file('Release')
        self.assert_equals_long(expected, actual)

    def test_writer_outer_release(self):
        handle = LazyWriter(pjoin(self.search_path, 'data', 'Release'))
        print >> handle, 'testing123'
        handle.close()

        release_path = pjoin(self.search_path, 'Release')
        release_handle = LazyWriter(release_path)
        self.writer.write_outer(release_handle)
        release_handle.close()

        expected_release = """Origin: Debian
Label: Debian2
Suite: happy
Version: 3.0r4
Codename: woody
Date: Wed, 22 Mar 2005 21:20:00 UTC
Architectures: alpha i386
Components: main contrib
Description: Hello World!
MD5Sum:
 bad9425ff652b1bd52b49720abecf0ba               11 data/Release
SHA1:
 e3dc8362c1586e4d9702ad862f29b6bef869afde               11 data/Release
"""
        actual_release = self.read_file(release_path)
        # Newer versions of apt-ftparchive put more sums after the file.
        # We'll overlook these for now, for compatibility purposes.
        edited_release = ''.join(actual_release.splitlines(True)[:13])
        self.assert_equals_long(expected_release, edited_release)

# vim:set ai et sw=4 ts=4 tw=75:
