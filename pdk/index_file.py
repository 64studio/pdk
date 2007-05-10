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

'''
IndexWriter and IndexFile write and read respectively a simple file
format for storing and later indexing a large number of small pickled
objects. The objects cannot refer to one another, however, the objects
can themselves be small trees of objects, so long as there are no
inter-object-tree relationships (at least direct ones).

'''

import os
import struct
from cPickle import Pickler, Unpickler
from pdk.exceptions import SemanticError, InputError

def pack_offset(number):
    '''Pack the number into an 8 byte string.'''
    return struct.pack('Q', number)

def unpack_offset(string, offset):
    '''Unpack an 8 byte number from a string offset.'''
    return struct.unpack('Q', string[offset:offset + 8])[0]

def read_offset(handle):
    '''Read an 8 byte number from a file handle.'''
    return unpack_offset(handle.read(8), 0)

class IndexWriter(object):
    '''Build up a persitent index containing individually pickled objects.

    filename - filename containing the index

    To use:
    writer = IndexWriter(filename)
    writer.init()
    many times:
        addresses = writer.add(object)
        writer.index([ keys ], addresses)
        writer.index([ more, keys], addresses)
    writer.terminate()
    '''
    def __init__(self, filename):
        self.filename = filename
        self.index_table = {}
        self.handle = None
        self.pickler = None

    def init(self):
        '''Actually open (truncate) the file and write header.'''
        self.handle = open(self.filename, 'w')
        self.handle.write('pdko' + struct.pack('>I', 1))
        self.handle.write(pack_offset(0))
        self.pickler = Pickler(self.handle, 2)

    def terminate(self):
        '''Writes object indexes and closes the file.'''
        key_dict = {}

        for key, address_list in self.index_table.iteritems():
            list_offset = self.handle.tell()
            key_dict[key] = list_offset
            self.pickler.clear_memo()
            self.pickler.dump(address_list)

        table_offset = self.handle.tell()
        self.pickler.clear_memo()
        self.pickler.dump(key_dict)

        self.handle.seek(8)
        self.handle.write(pack_offset(table_offset))
        self.handle.close()

    def add(self, *objects):
        '''Add a group objects.

        Returns an essentially opaque addresses object which should be
        passed to index.
        '''
        addresses = []
        for obj in objects:
            addresses.append(self.handle.tell())
            self.pickler.clear_memo()
            self.pickler.dump(obj)
        return tuple(addresses)

    def index(self, keys, addresses):
        '''Associate the given keys with the objects found at addressees.
        '''
        for key in keys:
            address_list = self.index_table.setdefault(key, [])
            address_list.append(addresses)

class IndexFileMissingError(SemanticError):
    '''Indicates that we tried to open a non existant IndexFile.'''
    pass

class IndexFormatError(InputError):
    '''Indicates that the magic bytes of an IndexFile are incorrect.'''
    pass

class IndexFile(object):
    '''Open an index file for reading.

    filename - the file containing the index.

    Use the get and get_all method to return objects in the index.
    '''
    def __init__(self, filename):
        if not os.path.exists(filename):
            raise IndexFileMissingError(filename)
        self.filename = filename
        self.handle = open(self.filename)
        self.unpickler = Unpickler(self.handle)
        magic = self.handle.read(8)
        expected_magic = 'pdko\x00\x00\x00\x01'
        if magic != expected_magic:
            message = 'Magic bytes incorrect. Is %s really a pdko file?' \
                      % self.filename
            raise IndexFormatError, message
        table_offset = read_offset(self.handle)
        self.handle.seek(table_offset)
        self.key_dict = self.unpickler.load()

    def iter_addresses(self, key):
        '''Get a list of pickle addresses for the given key.'''
        try:
            list_offset = self.key_dict[key]
            self.handle.seek(list_offset)
            address_list = self.unpickler.load()
            for addresses in address_list:
                yield addresses
        except KeyError:
            return

    def get(self, key, column):
        '''The columnth object for all object groups under they key.'''
        for addresses in self.iter_addresses(key):
            offset = addresses[column]
            self.handle.seek(offset)
            yield self.unpickler.load()

    def get_all(self, key):
        '''Get the full object group count for the key.'''
        for addresses in self.iter_addresses(key):
            objects = []
            for offset in addresses:
                self.handle.seek(offset)
                objects.append(self.unpickler.load())
            yield tuple(objects)

    def count(self, key):
        '''Get the object group count for the given key.'''
        return len(list(self.iter_addresses(key)))

# vim:set ai et sw=4 ts=4 tw=75:
