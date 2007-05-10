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

"""
cache.py

Manage a cache of packages and other files, all for use
when referenced by component descriptors.

Cache is indexed by 'blob', which is currently an sha1
checksum.

Cache contains .header files.
"""

__revision__ = "$Progeny$"

import os
import os.path
import stat
import re
from stat import ST_INO, ST_SIZE
import sha
import md5
import gzip
import pycurl
from shutil import copy2
from urlparse import urlparse
from tempfile import mkstemp
from pdk.package import get_package_type
from pdk.util import ensure_directory_exists, make_path_to, get_remote_file
from pdk.exceptions import SemanticError, ConfigurationError

# Debugging aids
import pdk.log

log = pdk.log.get_logger()

def calculate_checksums(file_path):
    """Calculate both sha-1 and md5 checksums for a file, returned
    as blob_ids
    """
    readsize = (1024 * 16)
    md5_calc = md5.new()
    sha1_calc = sha.new()
    input_file = open(file_path)
    while True:
        block = input_file.read(readsize)
        if not block:
            break
        md5_calc.update(block)
        sha1_calc.update(block)
    input_file.close()
    return 'sha-1:' + sha1_calc.hexdigest(), \
           'md5:' + md5_calc.hexdigest()

class CacheImportError(SemanticError):
    """Generic error for trouble importing to cache"""
    pass

########################################################################
class SimpleCache(object):
    """A moderately dumb data structure representing a physical cache
    directory on disk.

    Special capabilities are:
        1) the naming algorithm for file paths
        2) Checksumming & linking of contents by md5/sha1
        3) Awareness and use of a backing cache
    """

    def __init__(self, cache_path):
        self.path = os.path.abspath(cache_path)
        if os.path.exists(cache_path) and not os.path.isdir(cache_path):
            raise ConfigurationError("%s is not a directory path"
                                     % cache_path)
        # Check for a backing cache
        backing_path = os.path.join(cache_path, '.backing')
        if os.path.exists(backing_path):
            self.backing = SimpleCache(backing_path)
        else:
            self.backing = None

    def make_relative_filename(self, filename):
        """Calculate where the file should exist within the cache"""
        filename = os.path.split(filename)[1] or filename
        dirpath = '.'
        if ':' in filename:
            # md5 or sha-1 sum
            scheme, name = filename.split(':')
            dirpath = os.path.join(scheme, name[:2])
        # Note: else path is just ./filename
        return os.path.join(dirpath, filename)

    def file_path(self, filename):
        """Calculate the full file path (not absolute) for a file"""
        return os.path.join(
            self.path
            , self.make_relative_filename(filename)
            )

    def __contains__(self, filepath):
        """Determine if the cache already contains a file"""
        result = False
        if filepath and not os.path.basename(filepath).startswith('.'):
            local_path =  self.file_path(filepath)
            result = os.path.exists(local_path)
        return result

    def send_via_framer(self, blob_id, framer, callback_adapter):
        '''Send a blob via the given framer.'''
        cache_file = self.file_path(blob_id)
        mtime = os.stat(cache_file)[stat.ST_MTIME]
        handle = open(cache_file)
        framer.write_frame(blob_id)
        framer.write_handle(handle, callback_adapter)
        handle.close()
        framer.write_stream([str(mtime)])

    def import_from_framer(self, framer, mass_progress):
        '''Import a blob via the given framer.'''
        while True:
            local_filename = None
            try:
                first = framer.read_frame()
                if first == 'done':
                    framer.assert_end_of_stream();
                    break
                blob_id = first
                local_filename = self.make_download_filename()
                handle = open(local_filename, 'w')

                progress = mass_progress.get_single_progress(blob_id)
                total = mass_progress.get_size(blob_id)
                current = 0
                progress.start()
                for frame in framer.iter_stream():
                    current += len(frame)
                    handle.write(frame)
                    progress.write_bar(total, current)
                progress.done()
                handle.close()
                mtime = int(framer.read_frame())
                framer.assert_end_of_stream()
                if mtime != -1:
                    os.utime(local_filename, (mtime, mtime))
                self.incorporate_file(local_filename, blob_id)
                mass_progress.note_finished(blob_id)
                mass_progress.write_progress()
            finally:
                if local_filename and os.path.exists(local_filename):
                    os.unlink(local_filename)

    def import_file(self, locator, mass_progress):
        '''Download and incorporate a potentially remote source.

        locator - A FileLocator

        If the locator has a blob_id, it is used to verify the correctness
        of the acquired file. If the blob_id is missing, the file is not
        verified.
        '''
        local_filename = self.make_download_filename()
        get_progress = mass_progress.get_single_progress
        progress = get_progress(locator.blob_id, locator.get_full_url())
        try:
            full_url = locator.get_full_url()
            parts = urlparse(full_url)
            scheme = parts[0]
            if scheme in ('file', ''):
                source_file = parts[2]
                try:
                    progress.start()
                    copy2(source_file, local_filename)
                    progress.done()
                    self.umask_permissions(local_filename)

                except IOError, e:
                    if e.errno == 2 and os.path.exists(local_filename):
                        raise CacheImportError('%s not found' % full_url)
                    else:
                        raise
            else:
                try:
                    get_remote_file(full_url, local_filename,
                                    progress = progress)
                except pycurl.error, msg:
                    raise CacheImportError('%s, %s' % (msg, full_url))
            self.incorporate_file(local_filename, locator.blob_id)
            mass_progress.note_finished(locator.blob_id)
            mass_progress.write_progress()
        finally:
            if os.path.exists(local_filename):
                os.unlink(local_filename)

    def _add_links(self, source, blob_ids):
        '''Create visible links to the blob contained in source.

        Assume the blob_ids are correct.
        '''
        seed = self.make_download_filename()
        try:
            # optimization opportunity
            # we could attempt linking directly from source
            # to visible link to save on a copy here.
            copy2(source, seed)
            for blob_id in blob_ids:
                filename = self.file_path(blob_id)
                if os.path.exists(filename):
                    continue
                make_path_to(filename)
                os.link(seed, filename)
        finally:
            os.unlink(seed)

    def umask_permissions(self, filename):
        '''Set the filename permissions according to umask.'''
        current_umask = os.umask(0)
        os.umask(current_umask)
        new_mode = 0666 & ~current_umask
        os.chmod(filename, new_mode)

    def make_download_filename(self):
        """Create a pathname convenient for creating files for
        later linkage into the cache.
        """

        # mkstemp actually creates the file, so we must enusre this can
        # succeed.
        ensure_directory_exists(self.path)
        temp_fd, temp_fname = mkstemp('.partial', '.', self.path)
        os.close(temp_fd)

        self.umask_permissions(temp_fname)

        return temp_fname

    def incorporate_file(self, filepath, blob_id):
        """Places a temp file in its final cache location,
        by md5 and sha1, and unlinks the original filepath.
        """
        # Link it according to the given blob ids - note: does
        # not affect backing cache
        if self.backing:
            blob_ids = self.backing.incorporate_file(filepath, blob_id)
        else:
            blob_ids = calculate_checksums(filepath)
            if blob_id:
                if not blob_id in blob_ids:
                    message = 'Checksum mismatch: %s vs. %s.' \
                              % (blob_id, str(blob_ids))
                    raise CacheImportError(message)

        self._add_links(filepath, blob_ids)
        return blob_ids

    def __iter__(self):
        for record in os.walk(self.path):
            filenames = record[2] # (dir, subdirs, filename)
            for filename in filenames:
                yield filename

    def get_inode(self, blob_id):
        """Return the inode of a file given blob_id"""
        filepath = self.file_path(blob_id)
        return os.stat(filepath)[ST_INO]

    def get_size(self, blob_id):
        """Return the inode of a file given blob_id"""
        filepath = self.file_path(blob_id)
        return os.stat(filepath)[ST_SIZE]

    def iter_sha1_ids(self):
        """Iterate over the list of all the sha-1 ids in this cache."""
        rexp = re.compile('sha-1:[a-fA-F0-9]+$')
        for filename in self:
            if rexp.match(filename):
                yield filename

    def get_index_file(self):
        '''Return a the path to the blob index file.'''
        index_file = os.path.join(self.path, 'blob_list.gz')
        return index_file

    def write_index(self):
        """Write an index file describing the contents of the cache."""
        index_file = self.get_index_file()
        handle = gzip.open(index_file, 'w')
        regex = re.compile('(sha-1:|md5:)[a-fA-F0-9]+$')
        for filename in self:
            if regex.match(filename):
                path = self.make_relative_filename(filename)
                size = self.get_size(filename)
                handle.write('%s %s %d\n' % (filename, path, size))
        handle.flush()
        handle.close()

class Cache(SimpleCache):
    """Manage and report on the contents of the cache

    Adds higher-level functions
    """
    def __init__(self, cache_path):
        SimpleCache.__init__(self, cache_path)
        ensure_directory_exists(self.path)


    def get_header_filename(self, blob_id):
        "Return the filename of a blob's header file"
        fname = self.file_path(blob_id) + '.header'
        return fname

    def add_header(self, header, blob_id):
        """ write a header to a file, identified by blob_id"""
        # Always start with a temp file
        temp_path = self.make_download_filename()
        try:
            # Fill it.
            open(temp_path, 'w').write(header)
            # Link it to the appropriate blob_id.header file
            filename = self.get_header_filename(blob_id)
            try:
                os.link(temp_path, filename)
            except OSError, msg:
                # file exists
                if msg.errno == 17:
                    pass
                else:
                    raise
        finally:
            # Get rid of the temp file
            os.unlink(temp_path)


    def load_package(self, blob_id, package_format):
        """Load the raw header data into memory from a package
        """
        package_type = get_package_type(format = package_format)
        header_file = self.get_header_filename(blob_id)

        # check if the header file is already present
        # don't bother with synchronization issues.
        if os.path.basename(header_file) not in self:
            # Suck the header out and install it
            blob_filename = self.file_path(blob_id)
            try:
                header = package_type.extract_header(blob_filename)
            except IOError, error:
                if error.errno == 2:
                    message = "Missing package file in file cache\n"
                    message += "ref = '%s'\n" % blob_id
                    message += "Consider running pdk download on any new "
                    message += "or recently modified components."
                    raise SemanticError, message
            self.add_header(header, blob_id)

        header = open(header_file).read()
        return package_type.parse(header, blob_id)

# vim:set ai et sw=4 ts=4 tw=75:
