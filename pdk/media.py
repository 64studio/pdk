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

'''
This module houses functionality related to sorting packages onto media.
'''

BREAK = '<BREAK>'

class PackageMediaItems(object):
    '''Iterate over tuples of (size, package).

    packages -  iterator for input packages
    '''
    def __init__(self, packages):
        self.packages = packages

    def __iter__(self):
        for package in self.packages:
            yield (package.size, package)

class Splitter(object):
    '''Divide packages across volumes of size volume_size.

    package_iterator    - iterator for input packages
    volume_size         - size of volumes
    '''
    def __init__(self, package_iterator, volume_size):
        self.iterator = package_iterator
        self.volume_size = volume_size

    def iter_volumes(self):
        '''Return an iterator over volumes.

        next() returns either a package or BREAK to indicate a volume
        break.
        '''
        current_volume_size = 0
        for size, package in self.iterator:
            current_volume_size += size
            if current_volume_size > self.volume_size:
                yield BREAK
                current_volume_size = size
            yield package

# vim:set ai et sw=4 ts=4 tw=75:
