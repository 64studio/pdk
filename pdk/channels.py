# $Progeny$
#
#   Copyright 2005, 2006 Progeny Linux Systems, Inc.
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
The outside world is divided into remote workspaces and channels.

Both of these break down into sections, which contain information about
available packages.

Remote workspaces are treated purely as piles of downloadable
blobs. Channels contain more information about the packages available,
and are useful as sources for resolving.

The result of parsing configuration is a WorldData object.

OutsideWorldFactory consumes WorldData to create OutsideWorld.

OutsideWorld is able to filter all known packages by channel name and
provides a filtered iterator to do so.

OutsideWorld is also able to provide appropriate locator objects for a
given blob_id.

Locators take care of providing urls where packages may be
downloaded. They also take care of finding new locators for extra
files needed by dsc packages.

"""

import os
import stat
pjoin = os.path.join
import re
from urlparse import urlsplit
from gzip import GzipFile
from md5 import md5
try:
    import apt_pkg
except ImportError:
    pass
from xml.parsers.expat import ExpatError
from pdk.exceptions import InputError, SemanticError
from pdk.util import cpath, gen_file_fragments, get_remote_file, \
     shell_command, Framer, cached_property, parse_xml
from pdk.yaxml import parse_yaxml_file
from pdk.package import parse_rpm_header, deb, udeb, dsc, \
     get_package_type, UnknownPackageTypeError
from pdk.progress import ConsoleMassProgress
from pdk.index_file import IndexWriter, IndexFile, IndexFileMissingError
from pdk.log import get_logger

logger = get_logger()

def quote(raw):
    '''Create a valid filename which roughly resembles the raw string.'''
    return re.sub(r'[^A-Za-z0-9.-]+', '_', raw)

class MissingChannelDataError(SemanticError):
    '''Raised when a required channel data file is missing.

    Only used for real channels, not remote workspaces.
    '''
    pass

class LoaderFactory(tuple):
    '''Captures parameters to later create a cache loader.

    cls is the cache loader class. Remaining parameters are passed to
    the constructor of the cache loader.

    The objects should be memory efficient, comparable, and hashable.
    '''
    def create(loader_class, *params):
        '''Create a new loader factory object with the given params.'''
        return LoaderFactory((loader_class, tuple(params)))
    create = staticmethod(create)

    def create_loader(self, locators):
        '''Create a locator with the captured pa'''
        loader_class, params = self
        return loader_class(locators = locators, *params)

class URLCacheLoader(object):
    '''A cache loader which downloads raw files via curl or direct copy.
    '''
    def __init__(self, locators):
        self.locators = locators

    def load(self, cache, mass_progress):
        '''Import assigned blobs into the cache.

        Actually the framer strems zero blobs, as the "remote" side of
        the framer is downloading files directly into the cache.
        '''
        for locator in self.locators:
            if locator.blob_id not in cache:
                cache.import_file(locator, mass_progress)

class LocalWorkspaceCacheLoader(object):
    '''A cache loader for working with a remote workspace on this machine.
    '''
    def __init__(self, path, locators):
        self.path = path
        self.locators = locators

    def load(self, cache, mass_progress):
        '''Use a framer to stream the assigned blobs into a cache.'''
        blob_ids = [ l.blob_id for l in self.locators ]
        framer = Framer(*shell_command('pdk remote listen %s'
                                         % self.path))
        framer.write_stream(['pull-blobs'])
        framer.write_stream(blob_ids)
        framer.write_stream(['done'])
        cache.import_from_framer(framer, mass_progress)

class SshWorkspaceCacheLoader(object):
    '''A cache loader for working with a remote workspace via ssh.
    '''
    def __init__(self, host, path, locators):
        self.host = host
        self.path = path
        self.locators = locators

    def load(self, cache, mass_progress):
        '''Use a framer to stream the assigned blobs into a cache.'''
        blob_ids = [ l.blob_id for l in self.locators ]
        framer = Framer(*shell_command('ssh %s pdk remote listen %s'
                                         % (self.host, self.path)))
        framer.write_stream(['pull-blobs'])
        framer.write_stream(blob_ids)
        framer.write_stream(['done'])
        cache.import_from_framer(framer, mass_progress)

class FileLocator(object):
    '''Represents a resource which can be imported into the cache.'''
    def __init__(self, base_uri, filename, expected_blob_id, size,
                 factory):
        self.base_uri = base_uri
        self.filename = filename
        self.blob_id = expected_blob_id
        self.size = size
        self.loader_factory = factory

    def make_extra_file_locator(self, filename, expected_blob_id, size):
        '''Make a new locator which shares the base_uri or this locator.'''
        return FileLocator(self.base_uri, filename, expected_blob_id, size,
                           self.loader_factory)

    def __cmp__(self, other):
        return cmp((self.base_uri, self.filename, self.blob_id),
                   (other.base_uri, other.filename, other.blob_id))

    def get_full_url(self):
        '''Get the full url for the located file.'''
        parts = [ p for p in (self.base_uri, self.filename) if p ]
        return '/'.join(parts)

def make_comparable(cls, id_fields = None):
    '''Makes a class comparable on the given identity fields.

    If the id_fields are omitted then the class must provide a
    get_identity method which returns a tuple of values.
    '''
    if hasattr(cls, 'get_identity'):
        get_identity = cls.get_identity
    else:
        def get_identity(self):
            '''Return a tuple representing the "identity" of the object.'''
            identity = []
            for field in id_fields:
                identity.append(getattr(self, field))
            return tuple(identity)

    def __cmp__(self, other):
        class_cmp = cmp(self.__class__, other.__class__)
        if class_cmp:
            return class_cmp
        self_id = get_identity(self)
        other_id = get_identity(other)
        return cmp(self_id, other_id)

    def __hash__(self):
        return hash(get_identity(self))

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, get_identity(self))

    cls.__cmp__ = __cmp__
    cls.__hash__ = __hash__
    cls.__repr__ = __repr__
    cls.__str__ = __repr__

class RpmMdSection(object):
    '''Section for managing one rpm metadata repository.'''

    loader_factory = LoaderFactory.create(URLCacheLoader)

    def __init__(self, section_name, path, get_channel_file):
        self.section_name = section_name
        self.path = path
        self.get_channel_file = get_channel_file

        self.repomd_path = '/'.join([self.path, 'repodata', 'repomd.xml'])
        self.repomd_data = self.get_channel_file(self.repomd_path)

    def update(self):
        '''Grab the remote file and store it locally.'''
        get_remote_file(self.repomd_path, self.repomd_data, True)
        primary_path, primary_data = self.get_primary_data()
        get_remote_file(primary_path, primary_data, True)

    def get_primary_data(self):
        '''Look up the url and channel file for the primary.xml document.
        '''
        tree = parse_xml(open(self.repomd_data))
        root = tree.getroot()
        repo_prefix = 'http://linux.duke.edu/metadata/repo'
        data_pattern = '{%s}data' % repo_prefix
        data_elements = [ d for d in root.findall(data_pattern)
                          if d.attrib['type'] == 'primary' ]
        if len(data_elements) != 1:
            message = 'Found %d "primary" entries in %s' \
                % (len(data_elements), self.repomd_data)
            raise InputError, message

        data_element = data_elements[0]
        location_pattern = '{%s}location' % repo_prefix
        location_element = data_element.find(location_pattern)
        if location_element is None:
            raise InputError, 'Found no primary "location" in %s' \
                % self.repomd_data
        location = location_element.attrib['href']
        primary_url = '/'.join([self.path, location])
        return primary_url, self.get_channel_file(primary_url)

    def iter_package_info(self):
        '''Iterate over ghost_package, blob_id, locator for this section.
        '''
        dummy, primary_data = self.get_primary_data()
        handle = os.popen('gunzip <%s' % primary_data)
        tree = parse_xml(handle)
        handle.close()
        common_prefix = 'http://linux.duke.edu/metadata/common'
        for package_element in tree.getroot():
            package_tag = '{%s}%s' % (common_prefix, u'package')
            if package_element.tag != package_tag:
                message = u'Unexpected element "%s" in %s' \
                    % (package_element.tag, primary_data)
                logger.warn(message)
                continue

            package = parse_rpm_header(package_element)
            location_element = \
                package_element.find('{%s}location' % common_prefix)
            if location_element is None:
                message = "Can't find location for package %s." \
                    % package.name
                raise InputError, message
            location = location_element.attrib['href']
            locator = FileLocator(self.path, location, package.blob_id,
                                  package.size, self.loader_factory)

            yield package, dict(package), package.blob_id, locator

make_comparable(RpmMdSection, ('path',))

class AptDebSection(object):
    '''Section for managing a single Packages or Sources file.

    Requires a strategy object which controls whether the url will
    be treated as Packages or Sources.
    '''

    def __init__(self, full_path, channel_file, strategy):
        self.full_path = full_path
        self.channel_file = channel_file
        self.strategy = strategy

    def get_identity(self):
        '''Return an identity tuple for this object.'''
        return (self.strategy.package_type, self.full_path)

    def update(self):
        '''Grab the remote file and store it locally.'''
        get_remote_file(self.full_path, self.channel_file, True)

    def iter_package_info(self):
        '''Iterate over ghost_package, blob_id, locator for this section.
        '''
        if not os.path.exists(self.channel_file):
            raise MissingChannelDataError, self.channel_file
        tags_iterator = self.iter_apt_tags()
        for control, package in \
                self.iter_as_packages(tags_iterator):
            locator = self.strategy.get_locator(package)
            package.blob_id = locator.blob_id
            yield package, control, locator.blob_id, locator
            for extra_blob_id, extra_size, extra_filename \
                    in package.extra_files:
                make_extra = locator.make_extra_file_locator
                extra_locator = make_extra(extra_filename,
                                           extra_blob_id,
                                           extra_size)
                yield None, None, extra_blob_id, extra_locator

    def iter_apt_tags(self):
        '''Iterate over apt tag section objects in self.channel_file.'''
        handle = os.popen('gunzip <%s' % self.channel_file)
        apt_iterator = apt_pkg.ParseTagFile(handle)
        while apt_iterator.Step():
            yield apt_iterator.Section
        handle.close()

    def iter_as_packages(self, tags_iterator):
        """For each control stanza, yield the stanza and a package object.
        """
        for tags in tags_iterator:
            control = str(tags)
            yield control, self.strategy.package_type.parse_tags(tags,
                                                                 None)

make_comparable(AptDebSection, ('full_path', 'base_path'))

class AptDebBinaryStrategy(object):
    '''Handle get_locator and package_type for AptDebSection

    Used for Packages files.
    '''
    package_type = deb
    loader_factory = LoaderFactory.create(URLCacheLoader)

    def __init__(self, base_path):
        self.base_path = base_path

    def get_locator(self, package):
        """Return base, filename, blob_id for a package"""
        return FileLocator(self.base_path, package.pdk.raw_filename,
                           package.blob_id, package.size,
                           self.loader_factory)

class AptUDebBinaryStrategy(AptDebBinaryStrategy):
    '''Handle get_locator and package_type for AptDebSection

    Used for Packages files in debian-installer sections. (udebs)
    '''
    package_type = udeb

class AptDebSourceStrategy(object):
    '''Handle get_locator and package_type for AptDebSection

    Used for Sources files.
    '''
    package_type = dsc
    loader_factory = LoaderFactory.create(URLCacheLoader)

    def __init__(self, base_path):
        self.base_path = base_path

    def get_locator(self, package):
        """Return base, filename, blob_id for a package"""
        if ('deb', 'directory') in package:
            base = self.base_path + package[('deb', 'directory')]
        else:
            base = self.base_path
        return FileLocator(base, package.pdk.raw_filename, package.blob_id,
                           package.size, self.loader_factory)

def get_size(filename):
    '''Get the size of the given filename.'''
    return os.stat(filename)[stat.ST_SIZE]

class DirectorySection(object):
    '''Section object for dealing with local directories as channels.'''

    loader_factory = LoaderFactory.create(URLCacheLoader)

    def __init__(self, full_path):
        self.full_path = full_path

    def update(self):
        """Since the files are local, don't bother storing workspace state.
        """
        pass

    def iter_package_info(self):
        '''Iterate over ghost_package, blob_id, locator for this section.

        The directory is visited recursively and in a repeatable order.
        '''
        for root, dirnames, files in os.walk(self.full_path,
                                             topdown = True):
            dirnames.sort()
            files.sort()
            for candidate in files:
                full_path = pjoin(root, candidate)
                try:
                    package_type = get_package_type(filename = candidate)
                except UnknownPackageTypeError:
                    # if we don't know the the file is, we skip it.
                    continue
                control = package_type.extract_header(full_path)
                iterator = gen_file_fragments(full_path)
                md51_digest = md5()
                for block in iterator:
                    md51_digest.update(block)
                size = get_size(full_path)
                blob_id = 'md5:' + md51_digest.hexdigest()
                url = 'file://' + cpath(root)
                locator = FileLocator(url, candidate, blob_id, size,
                                      self.loader_factory)
                package = package_type.parse(control, blob_id)
                yield package, control, blob_id, locator
                for extra_blob_id, extra_size, extra_filename \
                        in package.extra_files:
                    make_extra = locator.make_extra_file_locator
                    extra_locator = make_extra(extra_filename,
                                               extra_blob_id,
                                               extra_size)
                    yield None, None, extra_blob_id, extra_locator


make_comparable(DirectorySection, ('full_path',))

class RemoteWorkspaceSection(object):
    '''Read the remote cache_info list from a source.'''
    def __init__(self, path, channel_file):
        self.full_path = path
        self.channel_file = channel_file

        parts = urlsplit(self.full_path)
        make_factory = LoaderFactory.create
        if parts[0] in ('http', 'https'):
            self.loader_factory = make_factory(URLCacheLoader)
        else:
            if parts[1]:
                self.loader_factory = make_factory(SshWorkspaceCacheLoader,
                                                    parts[1], parts[2])
            else:
                cache_loader_class = LocalWorkspaceCacheLoader
                self.loader_factory = make_factory(cache_loader_class,
                                                self.full_path)

    def update(self):
        '''A noop for this section type.

        Remote workspaces are updated at pull time.
        '''
        pass

    def iter_package_info(self):
        '''Iterate over blob_id, locator for this section.

        The package object is set to None as it is not know for this kind
        of section.
        '''
        cache_url = '/'.join([self.full_path, 'etc', 'cache'])
        if not os.path.exists(self.channel_file):
            return
        gunzipped = GzipFile(self.channel_file)

        for line in gunzipped:
            blob_id, blob_path, size_str = line.strip().split()
            size = int(size_str)
            locator = FileLocator(cache_url, blob_path, blob_id, size,
                                  self.loader_factory)
            yield None, None, blob_id, locator

make_comparable(RemoteWorkspaceSection, ('full_path',))

class WorldData(object):
    """Represents all configuration data known about the outside world.

    Contructed from a dict in in the form of:
        world_dict = {
            'local': { 'type': 'dir',
                       'path': '.../directory' },
            'remote': { 'type': 'apt-deb',
                        'path': 'http://baseaptrepo/',
                        'dist': 'stable',
                        'components': 'main contrib non-free',
                        'archs': 'source i386' },
            'source': { 'type': 'source',
                        'path': 'http://pathtosource/' }
         }

    Use this object as an iterator to get at the more useful form of the
    data.

    iter(world_data) -> [ name, data_dict]
    data_dict is the individual data_dict for the given channel or source.
    Each data_dict must have keys type and path. Certain types may require
    more keys.
    """
    def __init__(self, world_dict):
        self.world_dict = world_dict

    def load_from_stored(channel_data_file):
        '''Load and construct an object from file stored in a workspace.'''
        try:
            channels = parse_yaxml_file(channel_data_file)
        except ExpatError, message:
            raise InputError("In %s, %s" % (channel_data_file, message))
        except IOError, error:
            if error.errno == 2:
                channels = {}
        return WorldData(channels)

    load_from_stored = staticmethod(load_from_stored)

    def __iter__(self):
        for key, value in self.world_dict.iteritems():
            yield key, value

class OutsideWorldFactory(object):
    """Creates an OutsideWorld object from WorldData and a channel_dir."""
    def __init__(self, world_data, channel_dir, store_file):
        self.world_data = world_data
        self.channel_dir = channel_dir
        self.store_file = store_file

    def create(self):
        """Create and return the OutsideWorld object."""
        sections = {}

        for name, data_dict in self.world_data:
            sections[name] = []
            for section in self.iter_sections(name, data_dict):
                sections[name].append(section)

        return OutsideWorld(sections, self.store_file)

    def get_channel_file(self, path):
        """Get the full path to the file representing the given path."""
        return os.path.join(self.channel_dir, quote(path))

    def iter_sections(self, channel_name, data_dict):
        """Create sections for the given channel name and dict."""
        type_value = None
        try:
            type_value = data_dict['type']
        except KeyError, message:
            raise InputError('%s has no type' % channel_name)

        try:
            path = data_dict['path']
            if type_value == 'apt-deb':
                if path[-1] != "/":
                    message = "path in channels.xml must end in a slash"
                    raise InputError, message
                dist = data_dict['dist']
                nodists = dist[-1] == '/'
                if nodists:
                    components = ['']
                    if 'archs' in data_dict:
                        archs = data_dict['archs'].split()
                    if not archs:
                        archs = ('binary', 'source')
                else:
                    components = data_dict['components'].split()
                    archs = data_dict['archs'].split()

                for component in components:
                    for arch in archs:
                        # note that '/debian-installer' is treated as
                        # kind of "magic" here, because it is a magic name
                        # in debian repos.
                        if arch == 'source':
                            if '/debian-installer' in component:
                                continue
                            arch_part = 'source'
                            filename = 'Sources.gz'
                            strategy = AptDebSourceStrategy(path)
                        else:
                            arch_part = 'binary-%s' % arch
                            filename = 'Packages.gz'
                            if '/debian-installer' in component:
                                strategy = AptUDebBinaryStrategy(path)
                            else:
                                strategy = AptDebBinaryStrategy(path)

                        if nodists:
                            arch_part = ''
                            dists_part = ''
                        else:
                            dists_part = 'dists'

                        parts = [path[:-1], dists_part, dist, component,
                                 arch_part, filename]
                        parts = [ p for p in parts if p ]
                        full_path = '/'.join(parts)
                        channel_file = self.get_channel_file(full_path)
                        yield AptDebSection(full_path, channel_file,
                                            strategy)
            elif type_value == 'dir':
                yield DirectorySection(path)
            elif type_value == 'source':
                yield RemoteWorkspaceSection(path,
                                             self.get_channel_file(path))
            elif type_value == 'rpm-md':
                yield RpmMdSection(channel_name, path,
                                   self.get_channel_file)
            else:
                raise InputError('channel %s has unrecognized type %s'
                                 % (channel_name, type_value))
        except KeyError, field:
            message = 'channel "%s" missing field "%s"' % (channel_name,
                                                           str(field))
            raise InputError(message)

class WorldItem(object):
    '''Represents a single package/locator item in the outside world.

    Some items have no package object.

    When package is present it is a "ghost", meaning we can query it
    like a pdk.package.Package object, but we do not have a file in
    the cache backing it.
    '''
    def __init__(self, section_name, package, blob_id, locator):
        self.section_name = section_name
        self.package = package
        self.blob_id = blob_id
        self.locator = locator

class OutsideWorld(object):
    '''This object represents the world outside the workspace.'''
    def __init__(self, sections, store_file):
        self.sections = sections
        self.store_file = store_file

    def get_workspace_section(self, name):
        '''Get the named workspace section.'''
        if name not in self.sections:
            raise SemanticError('%s is not known workspace' % name)
        section = self.sections[name][0]
        if section.__class__ != RemoteWorkspaceSection:
            raise SemanticError('%s is a channel, not a workspace' % name)
        return section

    def get_backed_cache(self, cache):
        '''Return a ChannelBackedCache for this object and the given cache.
        '''
        return ChannelBackedCache(self.index, cache)

    def fetch_world_data(self):
        '''Update all remote source and channel data.'''
        for dummy, section in self.iter_sections():
            section.update()
        self.index_world_data()

    def index_world_data(self):
        '''Build the world_data index from channel data.'''
        logger.info('Building channel index...')
        self.index.build(self.iter_sections(), self.store_file)
        logger.info('Finished building channel index.')

    def __create_index(self):
        '''Get the IndexedWorldData object associated with this world.'''
        return IndexedWorldData(self.store_file)
    index = cached_property('index', __create_index)

    def get_limited_index(self, given_section_names):
        '''Return IndexedWorldData like object filtered by channel names.
        '''
        section_names = [ t[0]
                          for t in
                          self.iter_sections(given_section_names) ]
        return LimitedWorldDataIndex(self.index, section_names)

    def iter_sections(self, section_names = None):
        '''Iterate over stored sections for the given section_names.'''
        if not section_names:
            section_names = self.sections.keys()
            section_names.sort()
        for name in section_names:
            try:
                for section in self.sections[name]:
                    yield name, section
            except KeyError, e:
                raise InputError("Unknown channel %s." % str(e))

class PackageNotFoundError(SemanticError):
    '''Raised when a package cannot be found in any channel.'''
    pass

class ChannelBackedCache(object):
    '''Impersonate cache but use both channels and cache to load packages.
    '''
    def __init__(self, index, cache):
        self.index = index
        self.cache = cache

    def load_package(self, blob_id, type_string):
        '''Behave like Cache.load_packages.

        Tries to load from local cache before looking for a package object
        in the channels.
        '''
        if blob_id in self.cache:
            return self.cache.load_package(blob_id, type_string)

        package = self.index.get_package(blob_id, type_string)
        if package:
            return package

        message = "Can't find package (%s, %s).\n" % (type_string, blob_id)
        message += 'Consider reverting and reattempting this command.'
        raise PackageNotFoundError(message)

class IndexedWorldData(object):
    '''Wrap up storing all the channel data.

    Provides a number of field indexes on an otherwise too large list
    of WorldDataItems.
    '''
    def __init__(self, filename):
        self.filename = filename

    def __create_index_file(self):
        '''Get the index file object which underlies this object.'''
        try:
            return IndexFile(self.filename)
        except IndexFileMissingError:
            message = "Channel cache missing. " + \
                      "Run pdk channel update and try again."
            raise IndexFileMissingError, message
    index_file = cached_property('index_file', __create_index_file)

    def has_blob_id(self, blob_id):
        '''Does the given blob id appear in the world?'''
        return self.index_file.count(('ent-id', blob_id)) > 0

    def get_package(self, blob_id, type_string):
        '''Get a (ghost) package object for the blob_id.'''
        headers = self.index_file.get(('ent-id', blob_id), 1)
        for header in headers:
            if header is None:
                continue
            package_type = get_package_type(format = type_string)
            return package_type.parse(header, blob_id)

    def get_blob_ids(self, channel):
        '''Get a list of all blob_ids in the channel.'''
        try:
            return list(self.index_file.get(channel, 2))
        except IndexFileMissingError:
            # It's expected that this method will sometimes be called
            # before channel data has been indexed.
            return []

    def get_locator(self, blob_id):
        '''Get a locator object for the blob_id.'''
        locators = list(self.index_file.get(('ent-id', blob_id), 3))
        return locators[0]

    def iter_candidates(self, field, value, section_names):
        '''Iterate over WorldDataItems.

        Use the index named by key_field, with the given key. Return
        only the items found by that key.
        '''
        for section_name in section_names:
            key = (section_name, field, value)
            records = self.index_file.get_all(key)
            for item in self.iter_world_items(records, section_name):
                yield item

    def iter_channel_candidates(self, section_names):
        '''Get WorldItems for all the objects in the given channels.'''
        for channel in section_names:
            records = self.index_file.get_all(channel)
            for item in self.iter_world_items(records, channel):
                yield item

    def iter_world_items(records, section_name):
        '''Get WorldItems for all the objects in the given (one) channel.
        '''
        for type_string, header, blob_id, locator in records:
            if type_string and header:
                package_type = get_package_type(format = type_string)
                package = package_type.parse(header, blob_id)
                found_filename = os.path.basename(locator.filename)
                package['pdk', 'found-filename'] = found_filename
            else:
                package = None
            item = WorldItem(section_name, package, blob_id, locator)
            yield item
    iter_world_items = staticmethod(iter_world_items)

    def build(self, sections_iterator, index_file):
        '''Build up IndexedWorldData from the data in the given sections.
        '''
        indexed_field_names = ('name', 'sp-name', 'source-rpm', 'filename')
        indexed_fields = [ ('pdk', f) for f in indexed_field_names ]
        index_writer = IndexWriter(index_file)
        index_writer.init()
        try:
            for section_name, section in sections_iterator:
                section_iterator = section.iter_package_info()
                for ghost, header, blob_id, locator in section_iterator:
                    if ghost:
                        type_string = ghost.type
                    else:
                        type_string = None

                    addresses = index_writer.add(type_string, header,
                                                 blob_id, locator)
                    if ghost:
                        index_keys = []
                        for field in indexed_fields:
                            try:
                                value = ghost[field]
                            except KeyError:
                                continue
                            key = (section_name, field, value)
                            index_keys.append(key)
                        index_writer.index(index_keys, addresses)

                    ent_id_key = ('ent-id', blob_id)
                    channel_key = section_name
                    index_writer.index([ ent_id_key, channel_key ],
                                       addresses)
            index_writer.terminate()
            del index_writer
            # Next time index_file is accessed, it will be reloaded,
            # therefore actually reading the new file we just wrote!
            del self.index_file

        except MissingChannelDataError:
            message = 'Missing cached data. ' + \
                      'Consider running pdk channel update. ' + \
                      '(%s)' % section_name
            raise SemanticError(message)

class LimitedWorldDataIndex(object):
    '''Essentially impersonate IndexedWorldData but filter outputs.

    Does basically everything IndexedWorldData does, but all outputs are
    filtered by the given list of channel names.
    '''
    def __init__(self, data_index, channel_names):
        self.data_index = data_index
        self.channel_names = channel_names

    def iter_candidates(self, key_field, key):
        '''See IndexedWorldData.iter_candidates.

        Filters output by self.channel_names.
        '''
        return self.data_index.iter_candidates(key_field, key,
                                               self.channel_names)

    def iter_all_candidates(self):
        '''Iterate over all package candidates filtered by channel name.'''
        icc = self.data_index.iter_channel_candidates
        for item in icc(self.channel_names):
            if item.package:
                yield item

class MassAcquirer(object):
    '''Acquire blob_ids from multiple sources with one method call.

    This class allows for downloading a potentially large number of
    blob_ids from multiple sources all at once.
    '''
    def __init__(self, index):
        self.index = index
        self.data = []

    def add_blob(self, blob_id):
        '''Note the blob as a potential download candidate.'''
        self.data.append(blob_id)

    def get_locators(self, cache):
        '''Get needed locators for all noted blobs.

        Blob_ids already in the given cache are skipped.
        '''
        locators = []
        for blob_id in self.data:
            if blob_id not in cache:
                if self.index.has_blob_id(blob_id):
                    locator = self.index.get_locator(blob_id)
                    locators.append(locator)
                else:
                    raise SemanticError, \
                          "could not find %s in any channel" % blob_id
        return locators

    def get_cache_loaders(self, locators):
        '''Get a set of cache loaders for the given blob_ids.

        Each loader roughly corresponds to a download session.
        '''
        by_factory = {}
        for locator in locators:
            locator_list = \
                by_factory.setdefault(locator.loader_factory, [])
            locator_list.append(locator)

        cache_loaders = []
        for factory, locators in by_factory.iteritems():
            cache_loaders.append(factory.create_loader(locators))
        return cache_loaders


    def acquire(self, name, cache):
        '''Get cache loaders and use them to download package files.'''
        locators = self.get_locators(cache)
        size_map = {}
        for locator in locators:
            size_map[locator.blob_id] = int(locator.size)

        mass_progress = ConsoleMassProgress(name, size_map)
        for loader in self.get_cache_loaders(locators):
            loader.load(cache, mass_progress)

# vim:set ai et sw=4 ts=4 tw=75:
