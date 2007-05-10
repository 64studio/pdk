# $Progeny$
#
# Provide a file wrapper object for calculating hashes.
#
#   Copyright 2003 Progeny Linux Systems, Inc.
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

# This module provides a way to auto-update one or more Python hash
# calculators as I/O is performed on a file object.  Hash objects that
# conform to the standard interface for hash objects as implemented by
# Python's md5 and sha modules (as two examples) are supported.  Note
# that you should add the hash objects as soon as possible, before
# doing I/O, as hash objects will not be updated to account for I/O
# done previous to the object's being added.

class HashFile:
    def __init__(self, file_obj, hashes = ()):
        self.file = file_obj
        self.hash_list = list(hashes)
        self.closed = False
        self.propagate_close = False

    def __iter__(self):
        return self

    def next(self):
        result = self.readline()
        if result == "":
            raise StopIteration
        return result

    def _update_hashes(self, data):
        for obj in self.hash_list:
            obj.update(data)

    def _check_closed(self):
        if self.closed:
            raise IOError, "attempt to do I/O on a closed file"

    def _set_propagate_close(self):
        self.propagate_close = True

    def close(self):
        self.closed = True
        if self.propagate_close:
            self.file.close()

    def flush(self):
        self.file.flush()

    def isatty(self):
        return False

    def read(self, size = -1):
        self._check_closed()
        data = self.file.read(size)
        self._update_hashes(data)
        return data

    def readline(self, size = -1):
        self._check_closed()
        data = self.file.readline(size)
        self._update_hashes(data)
        return data

    def readlines(self, sizehint = -1):
        self._check_closed()
        if sizehint >= 0:
            data = self.file.readlines(sizehint)
        else:
            data = self.file.readlines()

        for line in data:
            self._update_hashes(line)

        return data

    def write(self, data):
        self._check_closed()
        self.file.write(data)
        self._update_hashes(data)

    def writelines(self, lines):
        self._check_closed()
        self.file.writelines(lines)
        for line in lines:
            self._update_hashes(line)

    def add_hash(self, hash_obj):
        self.hash_list.append(hash_obj)

    def remove_hash(self, hash_obj):
        self.hash_list.remove(hash_obj)

    def get_hashes(self):
        return tuple(self.hash_list)

def file(filename, mode = "r", bufsize = -1):
    f = __builtins__["open"](filename, mode, bufsize)
    h = HashFile(f)
    h._set_propagate_close()
    return h

open = file

# vim:set ai et sw=4 ts=4 tw=75:
