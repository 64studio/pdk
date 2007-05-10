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

from pdk.test.utest_util import TempDirTest
from pdk.index_file import IndexWriter, IndexFile, IndexFileMissingError, \
     IndexFormatError



class TestIndexFile(TempDirTest):
    def test_header(self):
        '''Make sure magic plus table address are present in files.'''
        open('a', 'w').write('as;dlfkja;ldskfjasd;lfkj')

        writer = IndexWriter('a')
        writer.init()
        writer.terminate()

        header = open('a').read(8)

        self.assert_equals('pdko\x00\x00\x00\x01', header)

    def test_bad_magic(self):
        open('a', 'w').write('as;dlfkja;ldskfjasd;lfkj')
        try:
            IndexFile('a')
        except IndexFormatError:
            pass

    def test_write_then_read(self):
        writer = IndexWriter('a')
        writer.init()

        address = writer.add('full', 'time', 3)
        writer.index([ ('a', 'b') ], address)

        address = writer.add(2, 7, 5)
        writer.index([ ('a', 'b'), ('z', 'c') ], address)
        writer.terminate()

        reader = IndexFile('a')
        self.assert_equal(['time', 7], list(reader.get(('a', 'b'), 1)))
        self.assert_equal([7], list(reader.get(('z', 'c'), 1)))
        self.assert_equal([], list(reader.get(('l', 'm'), 1)))

        self.assert_equal([ ('full', 'time', 3), (2, 7, 5) ],
                          list(reader.get_all(('a', 'b'))))
        self.assert_equal([ (2, 7, 5) ], list(reader.get_all(('z', 'c'))))
        self.assert_equal([], list(reader.get_all(('l', 'm'))))

        self.assert_equal(2, reader.count(('a', 'b')))
        self.assert_equal(1, reader.count(('z', 'c')))
        self.assert_equal(0, reader.count(('l', 'm')))

    def test_read_nonexistent(self):
        try:
            IndexFile('a')
            self.fail('nonexsistent index should trigger error.')
        except IndexFileMissingError:
            pass

# vim:set ai et sw=4 ts=4 tw=75:
