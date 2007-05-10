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

from pdk.channels import \
     DirectorySection, AptDebBinaryStrategy, AptDebSourceStrategy, \
     AptDebSection, OutsideWorldFactory, WorldData, quote

class MockPackage(object):
    def __init__(self, blob_id):
        self.blob_id = blob_id
        self.contents = {}

class TestChannelFilenames(Test):
    def test_iter_sections(self):
        world_dict = {
            'local': { 'type': 'dir',
                       'path': 'directory' },
            'remote': { 'type': 'apt-deb',
                        'path': 'http://localhost/',
                        'dist': 'stable',
                        'components': 'main contrib',
                        'archs': 'source i386' }
            }
        world_data = WorldData(world_dict)
        world = OutsideWorldFactory(world_data, 'z/z', 'a').create()
        base_path = 'http://localhost/'
        hpath = base_path + 'dists/stable/%s/%s/%s'
        expected = [
            ('local', DirectorySection('directory')),
            ('remote',
             AptDebSection(
                hpath % ('main', 'source', 'Sources.gz'),
                None,
                AptDebSourceStrategy(base_path))),
            ('remote',
             AptDebSection(
                hpath % ('main', 'binary-i386', 'Packages.gz'),
                None,
                AptDebBinaryStrategy(base_path))),
            ('remote',
             AptDebSection(
                hpath % ('contrib', 'source', 'Sources.gz'),
                None,
                AptDebSourceStrategy(base_path))),
            ('remote',
             AptDebSection(
                hpath % ('contrib', 'binary-i386', 'Packages.gz'),
                None,
                AptDebBinaryStrategy(base_path)))
            ]

        actual = list(world.iter_sections())
        self.assert_equals_long(expected, actual)

    def test_quote(self):
        path = 'http://localhost/dists/stable/Z.gz'
        quoted_path = 'http_localhost_dists_stable_Z.gz'

        self.assert_equals_long(quoted_path, quote(path))

# vim:set ai et sw=4 ts=4 tw=75:
