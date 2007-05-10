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
import os.path
from sets import Set
from pdk.test.utest_util import TempDirTest
from pdk.channels import FileLocator
from pdk.util import make_path_to
from pdk.progress import NullMassProgress
import pdk.cache

__revision__ = "$Progeny$"

class TestCache(TempDirTest):
    def test_construct(self):
        pdk.cache.Cache(os.path.join(self.work_dir, 'cache'))

    def test_cache_files(self):
        # This is being invalidated by changes in cache layout

        # Open a local file
        open('hi.txt', 'w').write('hello')

        # Copy it into the cache
        cache = pdk.cache.Cache(os.path.join(self.work_dir, 'cache'))
        cache.import_file(FileLocator('', 'hi.txt', None, None, None),
                          NullMassProgress())
        expected_blob_id = 'sha-1:aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d'
        cache_file = cache.file_path(expected_blob_id)
        assert os.path.exists(cache_file), cache_file+" expected"
        assert(expected_blob_id in cache)
        self.assert_equal(
            os.path.abspath('cache/md5/th/md5:this-one-md5')
            , os.path.abspath(cache.file_path('md5:this-one-md5'))
            )

    def test_acquire_file(self):
        """acquire file downloads the contents of the file_object.

        The contents should end up under the given tempoarary id.
        The return value should be new blob_ids."""

        open ('test', 'w').write('hello')
        cache = pdk.cache.Cache(os.path.join(self.work_dir, 'cache'))
        cache.import_file(FileLocator('', 'test', None, None, None),
                          NullMassProgress())
        expected_ids = ('sha-1:aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d',
                        'md5:5d41402abc4b2a76b9719d911017c592')
        for expected_id in expected_ids:
            assert os.path.exists(cache.file_path(expected_id))

    def test_incorporate_file(self):
        """incorporate_file renames a blob to its new blob_ids"""

        cache = pdk.cache.Cache(os.path.join(self.work_dir, 'cache'))
        blob_ids = ('sha-1:aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d',
                    'md5:5d41402abc4b2a76b9719d911017c592')
        filepath = cache.make_download_filename()
        open(filepath, 'w').write('hello')
        cache.incorporate_file(filepath, blob_ids[0])

        for blob_id in blob_ids:
            filename = cache.file_path(blob_id)
            assert os.path.exists(filename)
            self.assert_equal('hello', open(filename).read())
        assert not os.path.exists('cache/oldid')

    def test_cache_containment(self):
        """id in cache returns whether or not a file exists in the cache"""

        open ('test', 'w').write('hello')
        cache = pdk.cache.Cache(os.path.join(self.work_dir, 'cache'))
        cache.import_file(FileLocator('', 'test', None, None, None),
                          NullMassProgress())
        expected_ids = ('sha-1:aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d',
                        'md5:5d41402abc4b2a76b9719d911017c592')
        for expected_id in expected_ids:
            assert expected_id in cache

    def test_cache_iterator(self):
        """Test that files added to the cache show up in the iterator
        and are accessed correctly via 'in'
        """
        cache = pdk.cache.Cache(os.path.join(self.work_dir, 'cache'))
        make_path_to(cache.file_path('sha-1:someotherid'))
        open(cache.file_path('sha-1:someotherid'), 'w')\
                .write('helloalso')
        make_path_to(cache.file_path('md5:yetanotherid'))
        open(cache.file_path('md5:yetanotherid'), 'w') \
                .write('helloalso')
        contents = [ x for x in cache ]
        assert 'sha-1:someotherid' in cache
        assert 'sha-1:someotherid' in contents
        assert 'md5:yetanotherid' in cache
        assert 'md5:yetanotherid' in contents

    def test_get_inode(self):
        open ('test', 'w').write('hello')
        cache = pdk.cache.Cache(os.path.join(self.work_dir, 'cache'))
        cache.import_file(FileLocator('', 'test', None, None, None),
                          NullMassProgress())
        expected_ids = ('sha-1:aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d',
                        'md5:5d41402abc4b2a76b9719d911017c592')
        inodes = Set([ cache.get_inode(i) for i in expected_ids ])
        self.assert_equals(1, len(inodes))

    def test_get_header_filename(self):
        """header filename is blob_id + .header"""
        cache = pdk.cache.Cache(os.path.join(self.work_dir, 'cache'))
        self.assert_equal(
            os.path.abspath('cache/sha-1/a/sha-1:a.header'),
            os.path.abspath(cache.get_header_filename('sha-1:a'))
            )

# vim:set ai et sw=4 ts=4 tw=75:
